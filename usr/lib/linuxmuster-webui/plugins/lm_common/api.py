import os
import time
import ldap
import aj
import logging


class CSVSpaceStripper:
    def __init__(self, file, encoding='utf-8'):
        self.f = file
        self.encoding = encoding

    def close(self):
        self.f.close()

    def __iter__(self):
        return self

    def next(self):
        return self.f.next().decode(self.encoding, errors='ignore').strip()


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
        searchstring =  soph[0][1][field][0]
    except Exception as e:
        raise Exception('Field error. Either LDAP field does not exist or ajenti binduser does not have sufficient permissions:\n' 'Searched field was: ' + str(e) +' received information for filter:  ' + str(soph))
    l.unbind_s()
    return searchstring


