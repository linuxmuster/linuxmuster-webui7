import os
import time
import ldap
import aj
import logging
import subprocess
import json
import dpath


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
        #return self.f.next().decode(self.encoding, errors='ignore').strip()


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
        l.bind_s(params['binddn'],  params['bindpw'] )
    except Exception as e:
        logging.error(str(e))
        return False
    try:
        res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, searchFilter)
        userDN = res[0][0]
    except ldap.LDAPError, e:
        print e
    soph = l.search_s(
    userDN,
    ldap.SCOPE_SUBTREE,
    attrlist=[field],
    )
    try:
        resultString =  soph[0][1][field][0]
    except Exception as e:
        raise Exception('Field error. Either LDAP field does not exist or ajenti binduser does not have sufficient permissions:\n' 'Searched field was: ' + str(e) +' received information for filter:  ' + str(soph))
    l.unbind_s()
    return resultString

def lmn_getUserLdapValue(user, field):
    params = aj.config.data['linuxmuster']['ldap']
    searchFilter = "(&(cn=%s)(objectClass=user))" % user
    l = ldap.initialize('ldap://' + params['host'])
    try:
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.protocol_version = ldap.VERSION3
        l.bind_s(params['binddn'],  params['bindpw'] )
    except Exception as e:
        logging.error(str(e))
        return False
    try:
        res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, searchFilter)
        userDN = res[0][0]
    except ldap.LDAPError, e:
        print e
    soph = l.search_s(
    userDN,
    ldap.SCOPE_SUBTREE,
    attrlist=[field],
    )
    try:
        resultString =  soph[0][1][field][0]
    except Exception as e:
        raise Exception('Field error. Either LDAP field does not exist or ajenti binduser does not have sufficient permissions:\n' 'Searched field was: ' + str(e) +' received information for filter:  ' + str(soph))
    l.unbind_s()
    return resultString


def lmn_getSophomorixValue(sophomorixCommand, jsonpath):
    # only error log is going to be processed. standard output is thrown away
    jsonS =  subprocess.Popen(sophomorixCommand +' 1>/dev/null ',stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  shell=True).stdout.read()
    # ignore everything before the first {
    jsonS = jsonS[jsonS.find('{'):]
    jsonDict = json.loads(jsonS,encoding='latin1')
    try:
        # dpath slower but capability of complex jsonpaths -> test with 500 teachers no difference
        resultString = dpath.util.get(jsonDict, jsonpath)
        #resultString = (jsonDict[jsonpath])
    except Exception as e:
        raise Exception('Field error. Either sophomorix field does not exist or ajenti binduser does not have sufficient permissions:\n' 'Searched field was: ' + str(e) +' received information for filter:  ' + str(jsonObj))
    return resultString



def lmn_getUserSophomorixValue(user, field):
    #get json string from sophomorix
    jsonS =  subprocess.Popen('sophomorix-user --info --user '+ user + ' -jj 1>/dev/null',stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  shell=True).stdout.read()
    #parse string to dict
    jsonObj = json.loads(jsonS,encoding='latin1')
    try:
        resultString =  jsonObj['USERS'][user][field]
    except Exception as e:
        raise Exception('Field error. Either sophomorix field does not exist or ajenti binduser does not have sufficient permissions:\n' 'Searched field was: ' + str(e) +' received information for filter:  ' + str(jsonObj))
    return resultString
