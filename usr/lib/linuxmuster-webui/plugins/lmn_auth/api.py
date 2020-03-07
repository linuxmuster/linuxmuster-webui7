import logging
import ldap
import ldap.filter
import subprocess
from jadi import component
import pwd

import aj
from aj.auth import AuthenticationProvider, OSAuthenticationProvider
from aj.plugins.lmn_common.api import lmconfig, lmn_user_details

@component(AuthenticationProvider)
class LMAuthenticationProvider(AuthenticationProvider):
    id = 'lm'
    name = _('Linux Muster LDAP')



    def __init__(self, context):
        self.context = context

    def authenticate(self, username, password):
        if username == 'root':

            return OSAuthenticationProvider.get(self.context).authenticate(username, password)

        username = username.lower().encode('utf8')
        # get ajenti yaml parameters
        params = lmconfig.data['linuxmuster']['ldap']
        searchFilter = ldap.filter.filter_format("(&(cn=%s)(objectClass=user)(|(sophomorixRole=globaladministrator)(sophomorixRole=teacher)(sophomorixRole=schooladministrator) ))", [username])

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
        except ldap.LDAPError as e:
            print(e)


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

        ldappermissions = l.search_s(userDN,ldap.SCOPE_SUBTREE,attrlist=['sophomorixWebuiPermissionsCalculated'],)
        permissions = {}
        # convert python list we get from AD to dict
        if ldappermissions[0][1]: # is false if no values in SophomorixUserPermissions
            for b in ldappermissions[0][1]['sophomorixWebuiPermissionsCalculated']:
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
        # Activate with user context
        # systemString = ['sudo', 'sophomorix-passwd', '--user', username, '--pass', new_password, '--hide', '--nofirstpassupdate', '--use-smbpasswd']
        systemString = ['sophomorix-passwd', '--user', username, '--pass', new_password, '--hide', '--nofirstpassupdate', '--use-smbpasswd']
        subprocess.check_call(systemString, shell=False)

    def get_isolation_uid(self, username):
        """Returns the uid of the user which will run each worker."""

        # if username in ["root"] or 'administrator' in username:
        #     # Root context on the server
        #     return 0
        #
        # params = lmconfig.data['linuxmuster']['ldap']
        # searchFilter = "(&(cn=%s)(objectClass=user))" % username
        # l = ldap.initialize('ldap://' + params['host'])
        #
        # try:
        #     l.set_option(ldap.OPT_REFERRALS, 0)
        #     l.protocol_version = ldap.VERSION3
        #     l.bind_s(params['binddn'], params['bindpw'])
        # except Exception as e:
        #     logging.error(str(e))
        #     return False
        #
        # try:
        #     res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, searchFilter)
        #     userDN = res[0][0]
        # except Exception as e:
        #     # except ldap.LDAPError, e:
        #     print(e)
        #
        # try:
        #     if 'Teacher' in userDN:
        #         role = userDN.split(',')[1].split('=')[1].lower()[:-1]
        #         school = userDN.split(',')[2].split('=')[1]
        #     else:
        #         role = userDN.split(',')[2].split('=')[1].lower()[:-1]
        #         school = userDN.split(',')[3].split('=')[1]
        #     school_prefix = '' if school == 'default-school' else school + '-'
        #     posix_user = school_prefix + role
        #     # Return uid for defined role, e.g. teacher will returned uid from system user lmn7-teacher
        #     return pwd.getpwnam(posix_user).pw_uid
        # except:
        #     logging.error("Context user not found, running Webui as %s", 'nobody')
        #     return 65534
        return 0

    def get_profile(self, username):
        if username in ["root",None]:
            return {}
        try:
            profil = lmn_user_details(username)
            profil['isAdmin'] = "administrator" in profil['sophomorixRole']
            return profil
        except:
            return {}

