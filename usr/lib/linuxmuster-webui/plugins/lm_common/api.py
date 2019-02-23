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
        return self.f.next().decode(encoding='utf-8', errors='ignore').strip()
        # return self.f.next().decode(self.encoding, errors='ignore').strip()


def lm_backup_file(path):
    if not os.path.exists(path):
        return

    dir, name = os.path.split(path)
    backups = sorted([x for x in os.listdir(dir) if x.startswith('.%s.bak.' % name)])
    while len(backups) > 4:
        os.unlink(os.path.join(dir, backups[0]))
        backups.pop(0)

    with open(dir + '/.' + name + '.bak.' + str(int(time.time())), 'w') as f:
        f.write(open(path).read())


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


def lmn_getSophomorixValue(sophomorixCommand, jsonpath, ignoreErrors=False):
    jsonS = subprocess.Popen(sophomorixCommand, stderr=subprocess.PIPE, shell=False)
    data = ''
    record = 0
    jsonDict = {}
    while jsonS.poll() is None:
        output = jsonS.stderr.readline()
        output = output.replace("null", "\"null\"")
        if record == 1 :
            data += output.strip('\n')
        if '# JSON-begin' in output and '# JSON-end' in output:
            record = 1
            tmp = re.sub('# JSON-begin', '', output.strip('\n'))
            data += re.sub('# JSON.*', '', output.strip('\n'))
        elif '# JSON-begin' in output:
            record = 1
            data += re.sub('# JSON-begin', '', output.strip('\n'))
        elif '# JSON-end' in output:
            record = 0
            data += re.sub('# JSON.*', '', output.strip('\n'))
    if data:
        jsonDict = dict(jsonDict, **eval(data))
    data = ''

    ## Debug
    #with open('/var/log/getSophomorixValueDebugoutput.log', 'w') as f: 
    	#f.write(str(jsonDict))

    # if empty jsonpath is returned dont use dpath
    if jsonpath is '':

        return jsonDict
    if ignoreErrors is False:
        try:
            # Debug empty key string - > get json from file to test
            # dpath.options.ALLOW_EMPTY_STRING_KEYS=True
            # with open('/usr/lib/linuxmuster-webui/plugins/emptyStringKey.json') as json_data:
            #        jsonDict = json.load(json_data)
            #        #print(d)
            resultString = dpath.util.get(jsonDict, jsonpath)
            # file.write(str(resultString)+'\n')
        except Exception as e:
            pass
            raise Exception('getSophomorix Value error. Either sophomorix field does not exist or ajenti binduser does not have sufficient permissions:\n' +
                            'Error Message: ' + str(e) + '\n Dictionary we looked for information:\n  ' + str(jsonDict))
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


