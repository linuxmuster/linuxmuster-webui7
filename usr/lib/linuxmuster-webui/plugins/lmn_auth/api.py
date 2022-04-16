"""
Authentication classes to communicate with LDAP tree and load user's informations.
"""

import logging
import os
import stat
import pexpect
import re
import ldap
import ldap.filter
import ldap.modlist as modlist
import subprocess
import pwd
import grp
import simplejson as json
import yaml
import logging

from jadi import component, service
from aj.auth import AuthenticationProvider, OSAuthenticationProvider, AuthenticationService
from aj.config import UserConfigProvider
from aj.plugins.lmn_common.api import ldap_config as params, lmsetup_schoolname
from aj.plugins.lmn_common.multischool import SchoolManager
from aj.api.endpoint import EndpointError

@component(AuthenticationProvider)
class LMAuthenticationProvider(AuthenticationProvider):
    """
    LDAP Authentication provider for linuxmuster.net
    """

    id = 'lm'
    name = _('Linux Muster LDAP') # skipcq: PYL-E0602
    pw_reset = False

    def __init__(self, context):
        self.context = context

    def get_ldap_user(self, username, context=""):
        """
        Get the user's informations to initialize his session.

        :param username: Username
        :type username: string
        :param context: 'auth' to get permissions and 'userconfig' to get user's personal config, e.g. for Dashboard
        :type context: string
        :return: Dict of values
        :rtype: dict
        """

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
            'homeDirectory',
            'proxyAddresses',
            'sophomorixCustom1',
            'sophomorixCustom2',
            'sophomorixCustom3',
            'sophomorixCustom4',
            'sophomorixCustom5',
            'sophomorixCustomMulti1',
            'sophomorixCustomMulti2',
            'sophomorixCustomMulti3',
            'sophomorixCustomMulti4',
            'sophomorixCustomMulti5',
        ]

        if context == "auth":
            ldap_attrs.append('sophomorixWebuiPermissionsCalculated')

        if context == "userconfig":
            ldap_attrs = ['sophomorixWebuiDashboard']

        # Apply escape chars on username value
        searchFilter = ldap.filter.filter_format(ldap_filter, [username])

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

    def prepare_environment(self, username):
        # Initialize school manager
        active_school = self.get_profile(username)['activeSchool']
        schoolmgr = SchoolManager()
        schoolmgr.switch(active_school)
        self.context.schoolmgr = schoolmgr
 
        # Permissions for kerberos ticket
        uid = self.get_isolation_uid(username)

        if os.path.isfile(f'/tmp/krb5cc_{uid}'):
            os.unlink(f'/tmp/krb5cc_{uid}')

        if os.path.isfile(f'/tmp/krb5cc_{uid}{uid}'):
            os.rename(f'/tmp/krb5cc_{uid}{uid}', f'/tmp/krb5cc_{uid}')
            logging.warning(f"Changing kerberos ticket rights for {username}")
            os.chown(f'/tmp/krb5cc_{uid}', uid, 100)

    def _get_krb_ticket(self, username, password):
        """
        Get a new Kerberos ticket for username stored in /tmp/krb5cc_UIDUID
        This ticket will later be renamed as /tmp/krb5cc_UID.
        The reason is that this function is running as user nobody and cannot
        overwrite an existing ticket.

        :param username: Username
        :type username: string
        :param password: Password
        :type password: string
        """

        uid = self.get_isolation_uid(username)

        if uid == 0 and username == 'root':
            # No ticket for root user
            return

        logging.warning(f'Initializing Kerberos ticket for {username}')
        child = pexpect.spawn('/usr/bin/kinit', ['-c', f'/tmp/krb5cc_{uid}{uid}', username])
        child.expect('Password.*:')
        child.sendline(password)
        child.expect(pexpect.EOF)
        child.close()
        exit_code = child.exitstatus
        if exit_code:
            logging.error(f"Was not able to initialize Kerberos ticket for {username}")
            logging.error(f"{child.before.decode().strip()}")

    def authenticate(self, username, password):
        """
        Test credentials against LDAP and parse permissions for the session.

        :param username: Username
        :type username: string
        :param password: Password
        :type password: string
        :return: User's permissions
        :rtype: dict
        """

        if username == 'root':
            return OSAuthenticationProvider.get(self.context).authenticate(username, password)

        username = username.lower()

        # Does the user exist in LDAP ?
        try:
            userAttrs = self.get_ldap_user(username, context="auth")
        except KeyError as e:
            return False

        # Is the password right ?
        try:
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
                logging.error(str(e))
                raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(e))

        self._get_krb_ticket(username, password)

        return {
            'username': username,
            'password': password,
            'permissions': permissions,
            }

    def authorize(self, username, permission):
        """
        Get permissions from session, default false.

        :param username: Username
        :type username: string
        :param permission: Permission as dict
        :type permission: dict
        :return: Bool
        :rtype: bool
        """

        if username == 'root':
            return True
        return self.context.session.auth_info['permissions'].get(permission['id'], False)

    def change_password(self, username, password, new_password):
        """
        Change user password through sophomorix-passwd.

        :param username: Username
        :type username: string
        :param password: Old password
        :type password: string
        :param new_password: New password
        :type new_password: string
        """

        if not self.authenticate(username, password):
            raise Exception('Wrong password')
        systemString = ['sudo', 'sophomorix-passwd', '--user', username, '--pass', new_password, '--hide', '--nofirstpassupdate', '--use-smbpasswd']
        subprocess.check_call(systemString, shell=False)

    def get_isolation_gid(self, username):
        """
        For each session there will be an isolated worker. This function returns
        the right gid for the worker process.

        :param username: Username
        :type username: string
        :return: GID of the user
        :rtype: integer
        """

        if username == 'root':
            return 0
        # GROUP CONTEXT
        try:
            groupmembership = b''.join(self.get_ldap_user(username)['memberOf']).decode('utf8')
        except Exception:
            groupmembership = ''
        if 'role-globaladministrator' in groupmembership or 'role-schooladministrator' in groupmembership:
            return None

        roles = ['role-teacher', 'role-student']
        for role in roles:
            if role in groupmembership:
                try:
                    gid = grp.getgrnam(role).gr_gid
                    logging.debug(f"Running Webui as {role}")
                except KeyError:
                    gid = grp.getgrnam('nogroup').gr_gid
                    logging.debug(f"Context group not found, running Webui as {nogroup}")
                return gid
        return None

    def get_isolation_uid(self, username):
        """
        For each session there will be an isolated worker. This function returns
        the right uid for the worker process.

        :param username: Username
        :type username: string
        :return: UID of the user
        :rtype: integer
        """

        if username == 'root':
            return 0
        # USER CONTEXT
        try:
            groupmembership = b''.join(self.get_ldap_user(username)['memberOf']).decode('utf8')
        except Exception:
            groupmembership = ''

        if 'role-globaladministrator' in groupmembership or 'role-schooladministrator' in groupmembership:
            return 0

        try:
            uid = pwd.getpwnam(username).pw_uid
            logging.debug(f"Running Webui as {username}")
        except KeyError:
            uid = pwd.getpwnam('nobody').pw_uid
            logging.debug(f"Context user not found, running Webui as {nobody}")

        return uid

    def get_profile(self, username):
        """
        Prepare identity profile for angular.

        :param username: Username
        :type username: string
        :return: User's informations from LDAP
        :rtype: dict
        """

        if username in ["root",None]:
            return {'activeSchool': 'default-school'}
        try:
            profil = self.get_ldap_user(username)
            profil['isAdmin'] = b"administrator" in profil['sophomorixRole']
            # Test purpose for multischool
            if profil['sophomorixSchoolname'] == b'global':
                profil['activeSchool'] = "default-school"
            else:
                profil['activeSchool'] = profil['sophomorixSchoolname']

            if lmsetup_schoolname:
                profil['pageTitle'] = lmsetup_schoolname
            return json.loads(json.dumps(profil))
        except Exception as e:
            logging.error(e)
            return {}

    def check_mail(self, mail):
        # Search in the mail field, this must be discuted with others devs
        ldap_filter = """(&
                            (objectClass=user)
                            (|
                                (sophomorixRole=globaladministrator)
                                (sophomorixRole=schooladministrator)
                                (sophomorixRole=teacher)
                                (sophomorixRole=student)
                            )
                            (mail=%s)
                        )"""

        # Apply escape chars on mail value
        searchFilter = ldap.filter.filter_format(ldap_filter, [mail])

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
            res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, searchFilter, attrlist=['sAMAccountName'])
            if res[0][0] is None:
                # Don't show any hint if the email doesn't exists in ldap
                return False
            # What to do if email is not unique ?
            return res[0][1]['sAMAccountName'][0].decode()
        except (ldap.LDAPError, KeyError):
            return False

        l.unbind_s()
        return False

    def check_password_complexity(self, password):
        strong_pw = re.match('(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}', password)
        valid_pw = re.match('^[a-zA-Z0-9!@#§+\-$%&*{}()\]\[]+$', password)
        if valid_pw and strong_pw:
            return True
        raise EndpointError(_(
            f'Minimal length is 7 characters. Use upper, lower and special characters or numbers. (e.g. Muster!).' 
            f'Valid characters are: a-z A-Z 0-9 !§+-@#$%&amp;*( )[ ]{{ }}'))

    def update_password(self, username, password):
        systemString = ['sudo', 'sophomorix-passwd', '--user', username, '--pass', password, '--hide', '--nofirstpassupdate', '--use-smbpasswd']
        subprocess.check_call(systemString, shell=False)
        return True

@component(UserConfigProvider)
class UserLdapConfig(UserConfigProvider):
    """
    User config class compliant with linuxmuster.net LDAP config's scheme
    """

    id = 'lm'
    name = _('Linuxmuster LDAP user config') # skipcq: PYL-E0602

    def __init__(self, context):
        UserConfigProvider.__init__(self, context)
        self.context = context
        try:
            self.user = context.identity
        except AttributeError:
            self.user = None
        if self.user:
            self.load()
        else:
            self.data = {}

    def load(self):
        """
        Load attributes from LDAP.

        :return: User's attributes
        :rtype: yaml object if root or dict
        """

        if self.user == 'root':
            self.data = yaml.load(open('/root/.config/ajenti.yml'), Loader=yaml.SafeLoader)
        else:
            ## Load ldap attribute webuidashboard
            userAttrs = AuthenticationService.get(self.context).get_provider().get_ldap_user(self.user, context="userconfig")
            try:
                self.data = json.loads(userAttrs['sophomorixWebuiDashboard'])
            except Exception:
                logging.warning(
                    f'Error retrieving userconfig from {self.user}, '
                    f'value: {userAttrs["sophomorixWebuiDashboard"]}.'
                    f'This will be overwritten.'
                )
                self.data = {}

    def save(self):
        """
        Save user's config. If root, this goes in a file, otherwise in LDAP tree.
        """

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

            # Apply escape chars on self.user value
            searchFilter = ldap.filter.filter_format(ldap_filter, [self.user])
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
        """
        Change mode to "read, write, and execute by owner". Currently not used
        (self.path is not defined) but keeped in compatibility mode.
        """

        os.chmod(self.path, stat.S_IRWXU)
