import logging
import os
import stat

import ldap
import ldap.filter
import ldap.modlist as modlist
import subprocess
from jadi import component
import pwd
import grp
import simplejson as json
import yaml

import aj
from aj.auth import AuthenticationProvider, OSAuthenticationProvider, AuthenticationService
from aj.config import UserConfigProvider
from aj.plugins.lmn_common.api import lmconfig, lmsetup_schoolname

@component(AuthenticationProvider)
class LMAuthenticationProvider(AuthenticationProvider):
    id = 'lm'
    name = _('Linux Muster LDAP')

    def __init__(self, context):
        self.context = context

    def _get_ldap_user(self, username, context=""):
        """Retrieve user's DN and attributes from LDAP."""
        ldap_filter = """(&
                            (cn=%s)
                            (objectClass=user)
                            (|
                                (sophomorixRole=globaladministrator)
                                (sophomorixRole=schooladministrator)
                                (sophomorixRole=teacher)
                                (sophomorixRole=student)
                            )
                        )"""

        ldap_attrs = [
            'sophomorixQuota',
            'givenName',
            'DN',
            'sophomorixRole',
            'memberOf',
            'sophomorixAdminClass',
            'sAMAccountName',
            'sn',
            'mail',
            'sophomorixSchoolname',
        ]

        if context == "auth":
            ldap_attrs.append('sophomorixWebuiPermissionsCalculated')

        if context == "userconfig":
            ldap_attrs = ['sophomorixWebuiDashboard']

        searchFilter = ldap.filter.filter_format(ldap_filter, [username])
        params = lmconfig.data['linuxmuster']['ldap']

        l = ldap.initialize('ldap://' + params['host'])
        # Binduser bind to the  server
        try:
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.protocol_version = ldap.VERSION3
            l.bind_s(params['binddn'], params['bindpw'])
        except Exception as e:
            logging.error(str(e))
            raise KeyError(e)
        try:
            res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, searchFilter, attrlist=ldap_attrs)
            if res[0][0] is None:
                raise KeyError
            userAttrs = {
                attr:( value[0] if isinstance(value, list) and len(value) == 1 else value )
                for attr, value in res[0][1].items()
            }
            userAttrs['dn'] = res[0][0]
        except ldap.LDAPError as e:
            print(e)

        l.unbind_s()
        return userAttrs

    def authenticate(self, username, password):
        if username == 'root':
            return OSAuthenticationProvider.get(self.context).authenticate(username, password)

        username = username.lower()

        # Does the user exist in LDAP ?
        try:
            userAttrs = self._get_ldap_user(username, context="auth")
        except KeyError as e:
            return False

        # Is the password right ?
        try:
            params = lmconfig.data['linuxmuster']['ldap']
            l = ldap.initialize('ldap://' + params['host'])
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.protocol_version = ldap.VERSION3
            l.bind_s(userAttrs['dn'], password)
        except Exception as e:
            logging.error(str(e))
            return False

        webuiPermissions = userAttrs['sophomorixWebuiPermissionsCalculated']
        permissions = {}
        # convert python list we get from AD to dict
        for perm in webuiPermissions:
            module, value = perm.decode('utf-8').split(': ')
            try:
                permissions[module] = value == 'true'
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
        systemString = ['sudo', 'sophomorix-passwd', '--user', username, '--pass', new_password, '--hide', '--nofirstpassupdate', '--use-smbpasswd']
        subprocess.check_call(systemString, shell=False)

    def get_isolation_gid(self, username):
        """Returns the gid of the group which will run each worker."""
        if username == 'root':
            return 0
        # GROUP CONTEXT
        try:
            groupmembership = b''.join(self._get_ldap_user(username)['memberOf']).decode('utf8')
        except Exception as e:
            groupmembership = ''
        if 'role-globaladministrator' in groupmembership or 'role-schooladministrator' in groupmembership:
            return None

        roles = ['role-teacher', 'role-student']
        for role in roles:
            if role in groupmembership:
                try:
                    gid = grp.getgrnam(role).gr_gid
                    logging.debug("Running Webui as %s", role)
                except KeyError:
                    gid = grp.getgrnam('nogroup').gr_gid
                    logging.debug("Context group not found, running Webui as %s", 'nogroup')
                return gid
        return None

    def get_isolation_uid(self, username):
        """Returns the uid of the user which will run each worker."""
        if username == 'root':
            return 0
        # USER CONTEXT
        try:
            groupmembership = b''.join(self._get_ldap_user(username)['memberOf']).decode('utf8')
        except Exception as e:
            groupmembership = ''

        if 'role-globaladministrator' in groupmembership or 'role-schooladministrator' in groupmembership:
            return 0

        try:
            uid = pwd.getpwnam(username).pw_uid
            logging.debug("Running Webui as %s", username)
        except KeyError:
            uid = pwd.getpwnam('nobody').pw_uid
            logging.debug("Context user not found, running Webui as %s", 'nobody')
        return uid

    def get_profile(self, username):
        if username in ["root",None]:
            return {}
        try:
            profil = self._get_ldap_user(username)
            profil['isAdmin'] = b"administrator" in profil['sophomorixRole']
            if lmsetup_schoolname:
                profil['pageTitle'] = lmsetup_schoolname
            return json.loads(json.dumps(profil))
        except Exception as e:
            logging.error(e)
            return {}

@component(UserConfigProvider)
class UserLdapConfig(UserConfigProvider):
    id = 'lm'
    name = _('Linuxmuster LDAP user config')

    def __init__(self, context):
        UserConfigProvider.__init__(self, context)
        self.context = context
        try:
            self.user = context.identity
        except AttributeError as e:
            self.user = None
        if self.user:
            self.load()
        else:
            self.data = {}

    def load(self):
        if self.user == 'root':
            self.data = yaml.load(open('/root/.config/ajenti.yml'), Loader=yaml.Loader)
        else:
            ## Load ldap attribute webuidashboard
            userAttrs = AuthenticationService.get(self.context).get_provider()._get_ldap_user(self.user, context="userconfig")
            try:
                self.data = json.loads(userAttrs['sophomorixWebuiDashboard'])
            except Exception as e:
                logging.warning('Error retrieving userconfig from %s, value: %s. This will be overwritten', self.user, userAttrs['sophomorixWebuiDashboard'])
                self.data = {}

    def save(self):
        if self.user == 'root':
            with open('/root/.config/ajenti.yml', 'w') as f:
                f.write(yaml.safe_dump(
                    self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True
                ).decode('utf-8'))
            self.harden()
        else:
            ## Save ldap attribute webuidashboard
            ldap_filter = """(&
                            (cn=%s)
                            (objectClass=user)
                            (|
                                (sophomorixRole=globaladministrator)
                                (sophomorixRole=schooladministrator)
                                (sophomorixRole=teacher)
                                (sophomorixRole=student)
                            )
                        )"""
            ldap_attrs = ['sophomorixWebuiDashboard']

            searchFilter = ldap.filter.filter_format(ldap_filter, [self.user])
            params = lmconfig.data['linuxmuster']['ldap']
            with open('/etc/linuxmuster/.secret/administrator') as f:
                admin_pw = f.read()

            l = ldap.initialize('ldap://' + params['host'])
            # Binduser bind to the  server
            try:
                l.set_option(ldap.OPT_REFERRALS, 0)
                l.protocol_version = ldap.VERSION3
                l.bind_s("CN=Administrator,CN=Users,"+params['searchdn'], admin_pw)
            except Exception as e:
                logging.error(str(e))
                raise KeyError(e)
            try:
                res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, searchFilter, attrlist=ldap_attrs)
                if res[0][0] is None:
                    raise KeyError
                dn = res[0][0]
                userconfig_old = res[0][1]
            except ldap.LDAPError as e:
                print(e)

            userconfig_new = {'sophomorixWebuiDashboard': [json.dumps(self.data).encode()]}

            ldif = modlist.modifyModlist(userconfig_old,userconfig_new)
            l.modify_s(dn,ldif)
            l.unbind_s()

    def harden(self):
        os.chmod(self.path, stat.S_IRWXU)