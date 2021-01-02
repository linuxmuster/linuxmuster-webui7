"""
Common tools to communicate with sophomorix and handle config files.
"""

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
    """
    Check path before modifying files for security reasons.

    :param path: File to modify
    :type path: string
    :return: File path in allowed paths.
    :rtype: bool
    """

    allowed_path = False
    for rootpath in ALLOWED_PATHS:
        if rootpath in path:
            allowed_path = True
            break

    if allowed_path and '..' not in path:
        return True
    raise IOError(_("Access refused."))

class LinuxmusterConfig():
    """
    Basic class to handle linuxmuster webui's config file (yaml).
    """

    def __init__(self, path):
        self.data = None
        self.path = os.path.abspath(path)

    def __str__(self):
        return self.path

    def load(self):
        if os.geteuid() == 0:
            os.chmod(self.path, 384)  # 0o600
        self.data = yaml.load(open(self.path))

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True))

lmconfig = LinuxmusterConfig('/etc/linuxmuster/webui/config.yml')
lmconfig.load()

class CSVSpaceStripper:
    """
    CSV parser for linuxmuster's config files.
    """

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
    """
    Create a backup of a file if in allowed paths, but on ly keeps 10 backups.
    Backup files names scheme is `.<name>.bak.<timestamp>`

    :param path: Path of the file
    :type path: string
    """

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
    """
    Write CSV and backup csv file only if there's no difference with the original.
    Delimiter is always ';'
    DEPRECATED

    :param path: Path of the file
    :type path: string
    :param fieldnames: List of CSV fieldsnames
    :type fieldnames: list
    :param data: Data to write
    :type data: list of string
    :param encoding: Encoding, e.g. utf-8
    :type encoding: string
    """

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
    """
    Write config file it only if there's no difference with the original.

    :param path: Path of the file
    :type path: string
    :param data: New content
    :type data: string
    """

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
    """
    Worker for processing sophomorix commands.
    """

    def __init__(self, command):
        self.stdout = None
        self.stderr = None
        self.command = command
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        self.stdout, self.stderr = p.communicate()


def lmn_getSophomorixValue(sophomorixCommand, jsonpath, ignoreErrors=False):
    """
    Connector to all sophomorix commands. Run a sophomorix command with -j
    option (output as json) through a SophomorixProcess and parse the results.

    :param sophomorixCommand: Command with options to run
    :type sophomorixCommand: list
    :param jsonpath: Key to search in the resulted dict, e.g. /USERS/doe
    :type jsonpath: string
    :param ignoreErrors: Quiet mode
    :type ignoreErrors: bool
    :return: Whole output or key if jsonpath is defined
    :rtype: dict or value (list, dict, integer, string)
    """

    uid = os.getuid()
    if uid != 0:
        sophomorixCommand = ['sudo'] + sophomorixCommand

    # New Thread for one process to avoid conflicts
    t = SophomorixProcess(sophomorixCommand)
    t.daemon = True
    t.start()
    t.join()

    # Cleanup stderr output
    # output = t.stderr.replace(':null,', ":\"null\",")
    # TODO: Maybe sophomorix should provide the null value  in  a python usable format
    output = t.stderr.decode("utf8").replace(':null', ":\"null\"")
    output = output.replace(':null}', ":\"null\"}")
    output = output.replace(':null]', ":\"null\"]")


    # Some comands get many dicts, we just want the first
    output = output.replace('\n', '').split('# JSON-end')[0]
    output = output.split('# JSON-begin')[1]
    output = re.sub('# JSON-begin', '', output)

    # Convert str to dict
    jsonDict = {}
    if output:
        jsonDict = ast.literal_eval(output)

    # Without key, simply return the dict
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

