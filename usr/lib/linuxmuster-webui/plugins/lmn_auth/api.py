import logging
import ldap
import ldap.filter
import subprocess
from jadi import component
import pwd
import grp

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

        username = username.lower()
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
                i = b.decode('utf-8').split(': ')
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
        return self.context.session.auth_info['permissions'].get(permission['id'], False)

    def change_password(self, username, password, new_password):
        if not self.authenticate(username, password):
            raise Exception('Wrong password')
        # Activate with user context
        # systemString = ['sudo', 'sophomorix-passwd', '--user', username, '--pass', new_password, '--hide', '--nofirstpassupdate', '--use-smbpasswd']
        systemString = ['sophomorix-passwd', '--user', username, '--pass', new_password, '--hide', '--nofirstpassupdate', '--use-smbpasswd']
        subprocess.check_call(systemString, shell=False)

    def get_isolation_gid(self, username):
        """Returns the gid of the group which will run each worker."""
        # PREPARE FOR GROUP CONTEXT
        # try:
        #     groups = subprocess.check_output(['groups', username])
        # except subprocess.CalledProcessError as e:
        #     groups = e.output
        # for role_group in ['all-admins', 'all-teachers', 'all-students']:
        #     if role_group in groups:
        #         try:
        #             gid = grp.getgrnam(role_group).gr_gid
        #             logging.debug("Running Webui as %s", role_group)
        #         except KeyError:
        #             gid = grp.getgrnam('nogroup').gr_gid
        #             logging.debug("Context group not found, running Webui as %s", 'nogroup')
        #         return gid
        return None

    def get_isolation_uid(self, username):
        """Returns the uid of the user which will run each worker."""
        # PREPARE FOR USER CONTEXT
        # try:
        #     uid = pwd.getpwnam(username).pw_uid
        #     logging.debug("Running Webui as %s", username)
        # except KeyError:
        #     uid = pwd.getpwnam('nobody').pw_uid
        #     logging.debug("Context user not found, running Webui as %s", 'nobody')
        # return uid
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

