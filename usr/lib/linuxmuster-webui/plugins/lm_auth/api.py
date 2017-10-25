import logging
import ldap
import subprocess
from jadi import component

import aj
from aj.auth import AuthenticationProvider, OSAuthenticationProvider


@component(AuthenticationProvider)
class LMAuthenticationProvider(AuthenticationProvider):
    id = 'lm'
    name = _('Linux Muster LDAP')

    def __init__(self, context):
        self.context = context

    def authenticate(self, username, password):
        if username == 'root':

            return OSAuthenticationProvider.get(self.context).authenticate(username, password)

        # get ajenti yaml parameters
        params = aj.config.data['linuxmuster']['ldap']
        searchFilter = "(&(cn=%s)(objectClass=user))" % username

        l = ldap.initialize('ldap://' + params['host'])
        # Binduser bind to the  server
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
        l.unbind_s()

        #userbind
        try:
            l = ldap.initialize('ldap://' + params['host'])
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.protocol_version = ldap.VERSION3
            l.bind_s(userDN, password)

        except Exception as e:
            logging.error(str(e))
            return False

        ldappermissions = l.search_s(userDN,ldap.SCOPE_SUBTREE,attrlist=['SophomorixUserPermissions'],)
        permissions = {}
        # convert python list we get from AD to dict
        if ldappermissions[0][1]: # is false if no values in SophomorixUserPermissions
            for b in ldappermissions[0][1]['SophomorixUserPermissions']:
                i = b.split(': ')
                try:
                    i[1]
                    if i[1] == 'false': # translate strings to real bool values
                        i[1] = False
                    else:
                        i[1] = True
                    permissions[i[0]] = i[1]
                except Exception as e:
                    raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(e))
                    logging.error(str(e))

        return {
            'username': username,
            'password': password,
            'permissions': permissions,
            }

    def authorize(self, username, permission):
        if username == 'root':
            return True
        return self.context.session.auth_info['permissions'].get(permission['id'], permission['default'])

    def change_password(self, username, password, new_password):
        if not self.authenticate(username, password):
            raise Exception('Wrong password')
        subprocess.check_call('sophomorix-passwd -u %s --pass "%s"' % (username, new_password), shell=True)

    def get_isolation_uid(self, username):
        return 0

    def get_profile(self, username):
        return {}
