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
    params = aj.config.data['linuxmuster']['ldap']
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
    params = aj.config.data['linuxmuster']['ldap']
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
    # Attention! Also passwords and sensbile information get logged!!!
    debug = False
    # only error log is going to be processed. standard output is thrown away
    sophomorixCommand.append('1>/dev/null')
    file = open("/var/log/getSophomorixValueDebugoutput.log", "a")
    if debug:
        file.write('\n\n######New COMMAND #####\n\n')
        file.write(time.strftime("%c"))
        file.write('\n\n')
        file.write(str(sophomorixCommand)+'\n\n')
    else:
        file.write('\n\n######New COMMAND #####\n\n')
        file.write(time.strftime("%c"))
        file.write('\n\n')
        file.write('Debugging is disabled\n\n')

    jsonS = subprocess.Popen(sophomorixCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False).stdout.read()
    # jsonS is everything between sophomorix json headers
    # Use only if JSON-begin existst
    if '# JSON-begin' in jsonS:
        jsonS = jsonS.split("# JSON-begin", 1)[1]
        jsonS = jsonS.split("# JSON-end", 1)[0]
    # file.write(jsonS+'\n')
    jsonDict = json.loads(jsonS, encoding='UTF-8')

    if debug:
        file.write(str(jsonDict)+'\n\n\n')
    # if empty jsonpath is returned dont use dpath
    if jsonpath is '':

        if debug:
            file.write(str('no jsonpath return like it is:')+'\n\n')
            file.write(str(jsonDict)+'\n\n')
        file.close()
        return jsonDict
    if ignoreErrors is False:
        try:
            if debug:
                file.write(str('jsonpath')+'\n\n')
                file.write(str(jsonpath)+'\n\n')
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
    file.close()
    return resultString


def lmn_genRandomPW():
    regex = r"(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}"
    s = "@#$%^&*()?+-_"
    password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + str(s)) for _ in range(10))
    matches = re.search(regex, password)
    if matches:
        return password
    else:
        lmn_genRandomPW()
