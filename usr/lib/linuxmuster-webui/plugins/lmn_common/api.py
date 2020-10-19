import os
import time
import subprocess
import dpath
import re
import yaml
import threading
import ast
import unicodecsv as csv
import filecmp


ALLOWED_PATHS = [
                '/etc/linuxmuster/sophomorix/',     # used for school.conf or *.csv in lmn_settings, lmn_devices and lmn_users
                '/srv/linbo',                       # used in lmn_linbo for start.conf
                '/etc/linuxmuster/subnets-dev.csv'  # used in lmn_settings for subnets configuration
                ]

def check_allowed_path(path):
    """Check path before modifying file for security reasons."""
    allowed_path = False
    for rootpath in ALLOWED_PATHS:
        if rootpath in path:
            allowed_path = True
            break

    if allowed_path and '..' not in path:
        return True
    raise IOError(_("Access refused."))

class LinuxmusterConfig():
    def __init__(self, path):
        self.data = None
        self.path = os.path.abspath(path)

    def __str__(self):
        return self.path

    def load(self):
        self.data = yaml.load(open(self.path))

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True))

lmconfig = LinuxmusterConfig('/etc/linuxmuster/webui/config.yml')
lmconfig.load()

class CSVSpaceStripper:
    def __init__(self, file, encoding='utf-8'):
        self.f = file
        self.encoding = encoding
        # TODO : use self.comments to write the comments again in the file after modification
        self.comments = ""

    def close(self):
        self.f.close()

    def __iter__(self):
        return self

    def next(self):
        """For compatibility with PY2"""
        return self.__next__()

    def __next__(self):
        ## Store comments in self.comments
        nextline = self.f.readline()
        if nextline == '':
            raise StopIteration()
        while nextline.startswith('#'):
            self.comments += nextline
            nextline = self.f.readline()
        # Reader is unicodecsv, which needs bytes
        return nextline.encode('utf-8').strip()
        # return self.f.next().decode(self.encoding, errors='ignore').strip()


def lmn_backup_file(path):
    if not os.path.exists(path):
        return

    if check_allowed_path(path):
        dir, name = os.path.split(path)
        backups = sorted([x for x in os.listdir(dir) if x.startswith('.%s.bak.' % name)])
        while len(backups) > 10:
            os.unlink(os.path.join(dir, backups[0]))
            backups.pop(0)

        with open(dir + '/.' + name + '.bak.' + str(int(time.time())), 'w') as f:
            f.write(open(path).read())

def lmn_write_csv(path, fieldnames, data, encoding='utf-8'):
    """Write CSV and backup csv file only if there's no difference with the original. Delimiter is always ;"""

    if check_allowed_path(path):
        tmp = path + '_tmp'
        with open(tmp, 'wb') as f:
            csv.DictWriter(
                f,
                delimiter=';',
                fieldnames=fieldnames,
                encoding=encoding
            ).writerows(data)
        if not filecmp.cmp(tmp, path):
            lmn_backup_file(path)
            os.rename(tmp, path)
        else:
            os.unlink(tmp)

def lmn_write_configfile(path, data):
    """Write config file it only if there's no difference with the original."""

    if check_allowed_path(path):
        tmp = path + '_tmp'
        with open(tmp, 'w') as f:
            f.write(data)
        # check if file already exist before comparing
        if os.path.isfile(path):
            if not filecmp.cmp(tmp, path):
                lmn_backup_file(path)
                os.rename(tmp, path)
            else:
                os.unlink(tmp)
        else:
            os.rename(tmp, path)

class SophomorixProcess(threading.Thread):
    """Worker for processing sophomorix commands"""

    def __init__(self, command):
        self.stdout = None
        self.stderr = None
        self.command = command
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        self.stdout, self.stderr = p.communicate()


def lmn_getSophomorixValue(sophomorixCommand, jsonpath, ignoreErrors=False):
    """Get the response dict or value for a key after running a sophomorix command"""

    uid = os.getuid()
    if uid != 0:
        sophomorixCommand = ['sudo'] + sophomorixCommand

    ## New Thread for one process to avoid conflicts
    t = SophomorixProcess(sophomorixCommand)
    t.daemon = True
    t.start()
    t.join()

    ## Cleanup stderr output
    #output = t.stderr.replace(':null,', ":\"null\",")
    #TODO: Maybe sophomorix should provide the null value  in  a python usable format
    output = t.stderr.decode("utf8").replace(':null', ":\"null\"")
    output = output.replace(':null}', ":\"null\"}")
    output = output.replace(':null]', ":\"null\"]")


    ## Some comands get many dicts, we just want the first
    output = output.replace('\n', '').split('# JSON-end')[0]
    output = output.split('# JSON-begin')[1]
    output = re.sub('# JSON-begin', '', output)

    ## Convert str to dict
    jsonDict = {}
    if output:
        jsonDict = ast.literal_eval(output)

    ## Without key, simply return the dict
    if jsonpath is '':
        return jsonDict

    if ignoreErrors is False:
        try:
            resultString = dpath.util.get(jsonDict, jsonpath)
        except Exception as e:
            raise Exception('getSophomorix Value error. Either sophomorix field does not exist or ajenti binduser does not have sufficient permissions:\n' +
                            'Error Message: ' + str(e) + '\n Dictionary we looked for information:\n' + str(jsonDict))
    else:
        resultString = dpath.util.get(jsonDict, jsonpath)
    return resultString

