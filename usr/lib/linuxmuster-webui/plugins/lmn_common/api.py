import os
import time
import ldap
import aj
import logging
import subprocess
import json
import dpath
import string
import random
import re
import six
import yaml
import threading
import ast

from aj.auth import AuthenticationService

@six.python_2_unicode_compatible
class LinuxmusterConfig():
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
    def __init__(self, file, encoding='utf-8'):
        self.f = file
        self.encoding = encoding

    def close(self):
        self.f.close()

    def __iter__(self):
        return self

    def next(self):
        ## Ignore comments
        nextline = self.f.next()
        while nextline.startswith('#'):
            nextline = self.f.next()
        return nextline.decode(encoding='utf-8', errors='ignore').strip()
        # return self.f.next().decode(self.encoding, errors='ignore').strip()


def lmn_backup_file(path):
    if not os.path.exists(path):
        return

    dir, name = os.path.split(path)
    backups = sorted([x for x in os.listdir(dir) if x.startswith('.%s.bak.' % name)])
    while len(backups) > 4:
        os.unlink(os.path.join(dir, backups[0]))
        backups.pop(0)

    with open(dir + '/.' + name + '.bak.' + str(int(time.time())), 'w') as f:
        f.write(open(path).read())

def lmn_list_backup_file(path):
    if not os.path.exists(path):
        return

    backups = []
    dir, name = os.path.split(path)
    for x in os.listdir(dir):
        if x.startswith('.%s.bak.' % name):
            epoch = time.gmtime(int(x.split(".")[-1]))
            date  = time.strftime("%d/%m/%Y %H:%M:%S", epoch)
            backups.append({'path': x, 'date': date})
    return backups
    
def lmn_restore_backup_file(path, backup):
    if not os.path.exists(path) or not os.path.exists(backup):
        return

    dir, name = os.path.split(path)
    os.unlink(path)
    os.rename(backup, path)

def lmn_getLDAPGroupmembers(group, field):
    params = lmconfig.data['linuxmuster']['ldap']
    searchFilter = "(&(cn=%s)(objectClass=group))" % group
    l = ldap.initialize('ldap://' + params['host'])
    try:
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.protocol_version = ldap.VERSION3
        l.bind_s(params['binddn'],  params['bindpw'])
    except Exception as e:
        logging.error(str(e))
        return False
    try:
        res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, searchFilter)
        userDN = res[0][0]
    except Exception as e:
    # except ldap.LDAPError, e:
        print(e)
    soph = l.search_s(
    userDN,
    ldap.SCOPE_SUBTREE,
    attrlist=[field],
    )
    try:
        resultString = soph[0][1][field][0]
    except Exception as e:
        raise Exception('Field error. Either LDAP field does not exist or ajenti binduser does not have sufficient permissions:\n' 'Searched field was: ' + str(e) + ' received information for filter:  ' + str(soph))
    l.unbind_s()
    return resultString


def lmn_getUserLdapValue(user, field):
    params = lmconfig.data['linuxmuster']['ldap']
    searchFilter = "(&(cn=%s)(objectClass=user))" % user
    l = ldap.initialize('ldap://' + params['host'])
    try:
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.protocol_version = ldap.VERSION3
        l.bind_s(params['binddn'],  params['bindpw'])
    except Exception as e:
        logging.error(str(e))
        return False
    try:
        res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, searchFilter)
        userDN = res[0][0]
    except Exception as e:
    # except ldap.LDAPError, e:
        print(e)
    soph = l.search_s(
    userDN,
    ldap.SCOPE_SUBTREE,
    attrlist=[field],
    )
    try:
        resultString = soph[0][1][field][0]
    except Exception as e:
        raise Exception('Field error. Either LDAP field does not exist or ajenti binduser does not have sufficient permissions:\n' 'Searched field was: ' + str(e) + ' received information for filter:  ' + str(soph))
    l.unbind_s()
    return resultString

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

    ## New Thread for one process to avoid conflicts
    t = SophomorixProcess(sophomorixCommand)
    t.daemon = True
    t.start()
    t.join()

    ## Cleanup stderr output
    output = t.stderr.replace("null", "\"null\"")

    ## Some comands get many dicts, we just want the first
    output = output.replace('\n', '').split('# JSON-end')[0]
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

# check if the current user has a specific permissions
def lmn_checkPermission(permission):
    username = aj.worker.context.identity
    try:
        AuthenticationService.get(aj.worker.context).get_provider().authorize(username, permission)
        return True
    except:
        return False

def lmn_genRandomPW():
    regex = r"(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}"
    s = "@#$%^&*()?+-_"
    password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + str(s)) for _ in range(10))
    matches = re.search(regex, password)
    if matches:
        return password
    else:
        lmn_genRandomPW()
