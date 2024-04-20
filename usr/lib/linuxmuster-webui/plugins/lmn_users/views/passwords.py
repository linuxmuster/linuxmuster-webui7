"""
API for password management.
"""

import os
import subprocess

from jadi import component
from aj.api.http import get, post, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    def _checkPasswordPermissions(self, http_context, user):

        role_rank = {
            'globaladministrator': 4,
            'schooladministrator': 3,
            'teacher': 2,
            'student': 1,
            'examuser': 1,
        }

        identity = self.context.identity
        identity_role = self.context.ldapreader.getval(f'/users/{identity}', 'sophomorixRole')

        # Global admins have all rights
        if identity_role == 'globaladministrator':
            return True

        if user.endswith('-exam'):
            user_role = "examuser"
        else:
            user_role = self.context.ldapreader.getval(f'/users/{user}', 'sophomorixRole')

        ## Some additional security checks
        # Access forbidden for students
        if identity_role not in ['teacher', 'schooladministrator']:
            return False

        # Same role but other user -> access forbidden
        if identity_role == user_role:
            # User can only change its own password, not from someone else with the same role
            if identity != user:
                return False
        else:
            # Check if the role rank of the user is greater than the user logged in
            # If the role of the user can not be found, access forbidden
            if role_rank.get(user_role, 5) > role_rank[identity_role]:
                return False

        return True

    @get(r'/api/lmn/users/passwords/(?P<user>[^/]+)')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_user_get_password(self, http_context, user):
        """
        Get user's first password.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Output of `sophomorix-passwd`
        :rtype: dict
        """

        if not self._checkPasswordPermissions(http_context, user):
            return http_context.respond_forbidden()

        sophomorixCommand = ['sophomorix-user', '--info', '-jj', '-u', user]
        return lmn_getSophomorixValue(sophomorixCommand, '/USERS/'+user+'/sophomorixFirstPassword')

    @post(r'/api/lmn/users/passwords/reset-first')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_passwords_first(self, http_context):
        """
        Reset user's password to initial password.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Output of `sophomorix-passwd`
        :rtype: dict
        """

        users = http_context.json_body()['users']
        for user in users.split(','):
            # If one user fails the test, responding forbidden
            if not self._checkPasswordPermissions(http_context, user):
                return http_context.respond_forbidden()

        sophomorixCommand = ['sophomorix-passwd', '--set-firstpassword', '-jj', '-u', users, '--use-smbpasswd']
        return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')

    @post(r'/api/lmn/users/passwords/set-random')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_passwords_random(self, http_context):
        """
        Set a random password.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Output of `sophomorix-passwd`
        :rtype: dict
        """

        users = http_context.json_body()['users']
        for user in users.split(','):
            # If one user fails the test, responding forbidden
            if not self._checkPasswordPermissions(http_context, user):
                return http_context.respond_forbidden()

        # TODO: Password length should be read from school settings
        password_length = '8'
        sophomorixCommand = ['sophomorix-passwd', '-u', users, '--random', password_length, '-jj', '--use-smbpasswd']
        return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')

    @post(r'/api/lmn/users/passwords/set-first')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_passwords_set(self, http_context):
        """
        Set user's initial password.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Output of `sophomorix-passwd`
        :rtype: dict
        """

        users = http_context.json_body()['users']
        password = http_context.json_body()['password']

        for user in users.split(','):
            # If one user fails the test, responding forbidden
            if not self._checkPasswordPermissions(http_context, user):
                return http_context.respond_forbidden()

        sophomorixCommand = ['sophomorix-passwd', '-u', users, '--pass', password, '-jj', '--use-smbpasswd']
        return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN', sensitive=True)

    @post(r'/api/lmn/users/passwords/set-current')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_passwords_set_current(self, http_context):
        """
        Set user's actual password.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Output of `sophomorix-passwd`
        :rtype: dict
        """

        users = http_context.json_body()['users']
        password = http_context.json_body()['password']

        for user in users.split(','):
            # If one user fails the test, responding forbidden
            if not self._checkPasswordPermissions(http_context, user):
                return http_context.respond_forbidden()

        sophomorixCommand = ['sophomorix-passwd', '-u', users, '--pass', password, '--nofirstpassupdate', '--hide', '-jj', '--use-smbpasswd']
        return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN', sensitive=True)

    @get(r'/api/lmn/users/classes')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_get_classes(self, http_context):
        """
        Get list of all classes for teachers. Used in print password view.
        TODO : should maybe be moved in a more common api.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: With GET, list of classes, one classe per dict
        :rtype: With GET, list of dict
        """

        school = self.context.schoolmgr.school
        sophomorixCommand = ['sophomorix-query', '--class', '--schoolbase', school, '--group-full', '-jj']

        with authorize('lm:users:students:read'):
            # Check if there are any classes if not return empty list
            classes_raw = lmn_getSophomorixValue(sophomorixCommand, 'GROUP')
            classes = []
            for c, details in classes_raw.items():
                if details["sophomorixHidden"] == "FALSE":
                    classes.append(c)
            with authorize('lm:users:teachers:read'):
                # append empty element. This references to all users
                classes.append('')
                # add also teachers passwords
                if school == 'default-school':
                    classes.append('teachers')
                else:
                    classes.append(f'{school}-teachers')
            return classes

    @post(r'/api/lmn/users/passwords/print')
    @authorize('lm:users:teachers:read') #TODO
    @endpoint(api=True)
    def handle_api_users_print_individual(self, http_context):
        """
        Print individual passwords for selected users as PDF, one per page.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        school = self.context.schoolmgr.school
        users = http_context.json_body()['users']

        sophomorixCommand = [
            'sudo',
            'sophomorix-print',
            '--school', school,
            '--caller', self.context.identity,
            '--user', users,
            '--one-per-page',
            '-jj',
        ]

        # generate real shell environment for sophomorix print
        shell_env = {'TERM': 'xterm', 'SHELL': '/bin/bash',  'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',  'HOME': '/root', '_': '/usr/bin/python3'}
        try:
            subprocess.check_call(sophomorixCommand, shell=False, env=shell_env)
        except subprocess.CalledProcessError as e:
            return 'Error '+str(e)
        filename = f'user-{self.context.identity}.pdf'
        return filename

    @post(r'/api/lmn/users/print_csv')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_print_csv(self, http_context):
        """
        Print passwords as CSV
        Method POST: all passwords.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        school = self.context.schoolmgr.school

        user = http_context.json_body()['user']
        schoolclass = http_context.json_body()['schoolclass']

        # Trick: to avoid latex compilation and spare time, sending ls command, which does nothing
        sophomorixCommand = ['sudo', 'sophomorix-print', '--school', school, '--caller', str(user), '--command', 'ls']

        if schoolclass:
            sophomorixCommand.extend(['--class', schoolclass])
        # sophomorix-print needs the json parameter at the very end
        sophomorixCommand.extend(['-jj'])
        # check permissions
        if not schoolclass:
            # double check if user is allowed to print all passwords
            with authorize('lm:users:teachers:read'):
                pass
        # double check if user is allowed to print teacher passwords
        if schoolclass == 'teachers':
            with authorize('lm:users:teachers:read'):
                pass
        # generate real shell environment for sophomorix print
        shell_env = {'TERM': 'xterm', 'SHELL': '/bin/bash',  'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',  'HOME': '/root', '_': '/usr/bin/python3'}
        try:
            subprocess.check_call(sophomorixCommand, shell=False, env=shell_env)
        except subprocess.CalledProcessError as e:
            return f'Error {e}'
        return 'success'

    @post(r'/api/lmn/users/print')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_print(self, http_context):
        """
        Print passwords as PDF
        Method POST: all passwords.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        school = self.context.schoolmgr.school
        config_template = self.context.schoolmgr.custom_fields.get(
            'passwordTemplates', {'multiple': '', 'individual': ''}
        )
        config_template_individual = config_template.get('individual', '')
        config_template_multiple = config_template.get('multiple', '')

        user = http_context.json_body()['user']
        one_per_page = http_context.json_body()['one_per_page']
        pdflatex = http_context.json_body()['pdflatex']
        schoolclass = http_context.json_body()['schoolclass']
        template = ''

        sophomorixCommand = ['sudo', 'sophomorix-print', '--school', school, '--caller', str(user)]

        if one_per_page:
            try:
                template = http_context.json_body()['template_one_per_page']['path']
            except TypeError:
                template = config_template_individual
                if not template:
                    sophomorixCommand.extend(['--one-per-page'])
        else:
            try:
                template = http_context.json_body()['template_multiple']['path']
            except TypeError:
                template = config_template_multiple
        if template:
            sophomorixCommand.extend(['--template', template])
        if pdflatex:
            sophomorixCommand.extend(['--command'])
            sophomorixCommand.extend(['pdflatex'])
        if schoolclass:
            sophomorixCommand.extend(['--class', ','.join(schoolclass)])
        # sophomorix-print needs the json parameter at the very end
        sophomorixCommand.extend(['-jj'])
        # check permissions
        if not schoolclass:
            # double check if user is allowed to print all passwords
            with authorize('lm:users:teachers:read'):
                pass
        # double check if user is allowed to print teacher passwords
        if schoolclass == 'teachers':
            with authorize('lm:users:teachers:read'):
                pass
        # generate real shell environment for sophomorix print
        shell_env = {'TERM': 'xterm', 'SHELL': '/bin/bash',  'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',  'HOME': '/root', '_': '/usr/bin/python3'}
        try:
            subprocess.check_call(sophomorixCommand, shell=False, env=shell_env)
        except subprocess.CalledProcessError as e:
            return f'Error {e}'
        return 'success'
            # return lmn_getSophomorixValue(sophomorixCommand, 'JSONINFO')

    @get(r'/api/lmn/users/passwords/download/(?P<name>.+)')
    @authorize('lm:users:passwords')
    @endpoint(api=False, page=True)
    def handle_api_users_print_download(self, http_context, name):
        """
        Changes header to deliver a downloadable PDF.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param name: Name of the file
        :type name: string
        """

        root = '/var/lib/sophomorix/print-data/'
        path = os.path.abspath(os.path.join(root, name))

        if not path.startswith(root) or self.context.identity not in name:
            return http_context.respond_forbidden()
        return http_context.file(path, inline=False, name=name.encode())

    @get(r'/api/lmn/users/(?P<user>[a-z0-9\-_]*)/first-password-set')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_test_password(self, http_context, user):
        """
        Check if first password is still set.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param name: User's uid
        :type name: string
        :return: First password still set or not
        :rtype: bool
        """

        if not self._checkPasswordPermissions(http_context, user):
            return http_context.respond_forbidden()

        line = subprocess.check_output(['sudo', 'sophomorix-passwd', '--test-firstpassword', '-u', user]).splitlines()[-4]
        return b'1 OK' in line

    @get(r'/api/lmn/users/(?P<binduser>[a-z0-9\-_]*)/bindpassword')
    @authorize('lm:users:globaladmins:create')
    @endpoint(api=True)
    def handle_api_users_showpw_binduser(self, http_context, binduser):
        """
        Get the bind user's password.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string or list
        """

        if os.getuid() != 0:
            return EndpointReturn(403)

        secret_path = os.path.join('/etc/linuxmuster/.secret/', binduser)

        if os.path.isfile(secret_path):
            with open(secret_path, 'r') as f:
                return f.read()
