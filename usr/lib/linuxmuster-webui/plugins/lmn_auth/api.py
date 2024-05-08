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
from aj.plugins.lmn_common.api import ldap_config as params, lmsetup_schoolname, pwreset_config
from aj.plugins.lmn_common.multischool import SchoolManager
from aj.api.endpoint import EndpointError
from linuxmusterTools.ldapconnector import LMNLdapReader


@component(AuthenticationProvider)
class LMAuthenticationProvider(AuthenticationProvider):
    """
    LDAP Authentication provider for linuxmuster.net
    """

    id = 'lm'
    name = _('Linux Muster LDAP') # skipcq: PYL-E0602
    pw_reset = pwreset_config.get('activate', False)

    def __init__(self, context):
        self.context = context
        self.lr = LMNLdapReader

    def get_ldap_user(self, username, attributes=[]):
        """
        Get the user's informations to initialize his session.

        :param username: Username
        :type username: string
        :param context: 'auth' to get permissions and 'userconfig' to get user's personal config, e.g. for Dashboard
        :type context: string
        :return: Dict of values
        :rtype: dict
        """

        if username.endswith('-exam'):
            return self.lr.get(f'/users/exam/{username}', attributes=attributes)

        return self.lr.get(f'/users/{username}', attributes=attributes)

    def prepare_environment(self, username):
        """
        Perform some objects initialization (multischool environment, kerberos
        ticket) before switching to worker.

        :param username: sAMAccountName
        :type username: string
        """

        # Initialize school manager
        active_school = self.get_profile(username)['activeSchool']
        schoolmgr = SchoolManager()
        schoolmgr.switch(active_school)
        self.context.schoolmgr = schoolmgr
        self.context.ldapreader = LMNLdapReader

        def schoolget(*args, **kwargs):
            """
            This alias allow to automatically pass the school context for school
            specific requests.
            """

            result = self.context.ldapreader.get(*args,**kwargs, school=self.context.schoolmgr.school)
            return result

        self.context.ldapreader.schoolget = schoolget
 
        # Permissions for kerberos ticket
        uid = self.get_isolation_uid(username)

        if os.path.isfile(f'/tmp/krb5cc_{uid}{uid}'):
            if os.path.isfile(f'/tmp/krb5cc_{uid}'):
                os.unlink(f'/tmp/krb5cc_{uid}')

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

        krb_cache = f'/tmp/krb5cc_{uid}{uid}'

        try:
            subprocess.check_call(["klist", "-s", f'/tmp/krb5cc_{uid}'])
            return
        except subprocess.CalledProcessError as e:
            # Kerberos ticket not available, continuing
            pass

        try:
            logging.warning(f'Initializing Kerberos ticket for {username}')
            child = pexpect.spawn('/usr/bin/kinit', ['-c', krb_cache, username])
            child.expect('.*:', timeout=2)
            child.sendline(password)
            child.expect(pexpect.EOF)
            child.close()
            exit_code = child.exitstatus
            if exit_code:
                logging.error(f"Was not able to initialize Kerberos ticket for {username}")
                logging.error(f"{child.before.decode().strip()}")
        except pexpect.exceptions.TIMEOUT:
            logging.error(
                f"Was not able to initialize Kerberos ticket for {username}")

    def _check_password(self, username, password, dn=''):
        """
        Check username's password against LDAP server

        :param username: Username
        :type username: string
        :param password: Password
        :type password: string
        :param dn: User's DN
        :type dn: string
        :return: User's permissions
        :rtype: bool
        """

        if not dn:
            dn = self.get_ldap_user(username, attributes=['dn'])

        # Is the password right ?
        try:
            l = ldap.initialize('ldap://' + params['host'])
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.protocol_version = ldap.VERSION3
            l.bind_s(dn, password)
            return True
        except Exception as e:
            logging.error(str(e))
            return False

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
            userAttrs = self.get_ldap_user(username, attributes=['dn', 'sophomorixWebuiPermissionsCalculated', 'permissions'])
            if not userAttrs or not userAttrs.get('dn', ''):
                return False
            # TODO authorize access to exam users ?
            # if userAttrs.get('sophomorixRole', '') == 'examuser':
            #     return False
        except KeyError as e:
            return False

        if not self._check_password(username, password, dn=userAttrs['dn']):
            return False

        self._get_krb_ticket(username, password)

        return {
            'username': username,
            'password': password,
            'permissions': userAttrs['permissions'],
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

        if not username:
            return False

        ## When 2FA is activated, auth_info is missing in prepare_session
        ## Must be fixed in Ajenti
        auth_info = getattr(self.context.session, 'auth_info', None)
        if auth_info is None:
            permissions = {}
            webuiPermissions = self.lr.get(f'/users/{username}').get('sophomorixWebuiPermissionsCalculated', [])
            for perm in webuiPermissions:
                module, value = perm.split(': ')
                try:
                    permissions[module] = value == 'true'
                except Exception as e:
                    logging.error(str(e))
                    raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(e))

            # Populating session.auth_info for further use
            self.context.session.auth_info = {
                'username': username,
                'permissions':  permissions
            }

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
        subprocess.check_call(systemString, shell=False, sensitive=True)

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
            groupmembership = ''.join(self.get_ldap_user(username).get('memberOf', []))
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
            groupmembership = ''.join(self.get_ldap_user(username).get('memberOf', []))
        except Exception as e:
            logging.error(e)
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
            # Test purpose for multischool
            if profil['sophomorixSchoolname'] == 'global':
                profil['activeSchool'] = "default-school"
            else:
                profil['activeSchool'] = profil['sophomorixSchoolname']

            if lmsetup_schoolname:
                # TODO : use .self.context.schoolmgr.schoolname if available
                profil['schoolname'] = lmsetup_schoolname
            return json.loads(json.dumps(profil))
        except Exception as e:
            logging.error(e)
            return {}

    def check_mail(self, mail):
        """
        Check if a given mail actually exists in the LDAP tree, in order to send
        or not a password reset email.
        The tested field must be given in the config file.

        :param mail: Email of the user
        :type mail: basestring
        :return: Existing or not
        :rtype: bool
        """

        ldap_filter = f"""(&
                            (objectClass=user)
                            (|
                                (sophomorixRole=globaladministrator)
                                (sophomorixRole=schooladministrator)
                                (sophomorixRole=teacher)
                                (sophomorixRole=student)
                            )
                            ({pwreset_config['ldap_mail_field']}=%s)
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
        """
        Check if a given password for a user for the password reset function
        respects some standards.
        """

        strong_pw = re.match('(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()\+{}\-\[\]]|(?=.*\d)).{7,}', password)
        valid_pw = re.match('^[a-zA-Z0-9!@#§+\-$%&*{}()\]\[]+$', password)
        if valid_pw and strong_pw:
            return True
        raise EndpointError(_(
            f'Minimal length is 7 characters. Use upper, lower and special characters or numbers. (e.g. Muster!).' 
            f'Valid characters are: a-z A-Z 0-9 !§+-@#$%&amp;*( )[ ]{{ }}'))

    def update_password(self, username, password):
        systemString = ['sudo', 'sophomorix-passwd', '--user', username, '--pass', password, '--hide', '--nofirstpassupdate', '--use-smbpasswd']
        subprocess.check_call(systemString, shell=False, sensitive=True)
        return True

    def signout(self):
        """
        Perform some cleaning while destroying the session (removing the
        kerberos ticket).
        """

        uid = self.get_isolation_uid(self.context.identity)

        if uid == 0 and self.context.identity == 'root':
            # No ticket for root user
            return
        # Remove Kerberos ticket
        subprocess.check_output(['/usr/bin/kdestroy', '-c', f'/tmp/krb5cc_{uid}'])

@component(UserConfigProvider)
class UserLdapConfig(UserConfigProvider):
    """
    User config class compliant with linuxmuster.net LDAP config's scheme
    TODO : currently not used, must be updated
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
            userAttrs = AuthenticationService.get(self.context).get_provider().get_ldap_user(self.user)
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
