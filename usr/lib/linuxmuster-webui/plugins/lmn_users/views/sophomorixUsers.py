"""
APIs for the management of the sophomorix's users.
"""

import os

from jadi import component
from aj.api.http import get, post, patch, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.userStatus = {
            'A' : {'tag':'Activated', 'color':'success'},
            'U' : {'tag':'Usable', 'color':'success'},
            'P' : {'tag':'Permanent', 'color':'success'},
            'E' : {'tag':'Enabled', 'color':'success'},
            'S' : {'tag':'Self-activated', 'color':'success'},
            'T' : {'tag':'Tolerated', 'color':'info'},
            'L' : {'tag':'Locked', 'color':'warning'},
            'D' : {'tag':'Deactivated', 'color':'warning'},
            'F' : {'tag':'Frozen', 'color':'warning'},
            'R' : {'tag':'Removable', 'color':'danger'},
            'K' : {'tag':'Killable', 'color':'danger'},
            'X' : {'tag':'Exam', 'color':'danger'},
            'M' : {'tag':'Managed', 'color': 'info'},
        }

    @get(r'/api/lmn/sophomorixUsers/teachers((?P<user>/[a-z0-9\-_]*))?')
    @authorize('lm:users:teachers:read')
    @endpoint(api=True)
    def handle_api_sophomorix_teachers(self, http_context, user=None):
        """
        Get teachers list from LDAP tree.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param user: if provided, user to show (containing / at the beginning)
        :type user: str
        :return: List of teachers with details, one teacher per dict.
        :rtype: list of dict
        """

        schoolname = self.context.schoolmgr.school
        teachersList = []

        if user is None:
                # TODO: This could run with --user-basic but not all memberOf are filled. Needs verification
                sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-full', '-jj']
        else:
                sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-full', '-jj', '--sam', user[1:]]
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        if 'USER' in result.keys():
            teachers = result['USER']
            for _, details in teachers.items():
                if details['sophomorixStatus'] in self.userStatus.keys():
                    details['sophomorixStatus'] = self.userStatus[details['sophomorixStatus']]
                else:
                    details['sophomorixStatus'] = {'tag': details['sophomorixStatus'], 'color': 'default'}
                details['selected'] = False
                teachersList.append(details)
            return teachersList
        return ["none"]

    @get(r'/api/lmn/sophomorixUsers/students((?P<user>/[a-z0-9\-_]*))?')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_sophomorix_students(self, http_context, user=None):
        """
        Get students list from LDAP tree.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param user: if provided, user to show (containing / at the beginning)
        :type user: str
        :return: List of students with details, one student per dict.
        :rtype: list of dict
        """

        schoolname = self.context.schoolmgr.school

        studentsList = []
        if user is None:
            sophomorixCommand = ['sophomorix-query', '--student', '--schoolbase', schoolname, '--user-full', '-jj']
        else:
            # sophomorixCommand = ['sophomorix-query', '--student', '--schoolbase', schoolname, '--user-full', '-jj', '--sam', user]
            sophomorixCommand = ['sophomorix-query', '--user-full', '-jj', '--sam', user[1:]]
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        if 'USER' in result.keys():
            students = result['USER']
            for _, details in students.items():
                # TODO: get a better way to remove Birthay from user detail page
                details['sophomorixBirthdate'] = 'hidden'
                if details['sophomorixStatus'] in self.userStatus.keys():
                    details['sophomorixStatus'] = self.userStatus[details['sophomorixStatus']]
                else:
                    details['sophomorixStatus'] = {'tag': details['sophomorixStatus'], 'color': 'default'}
                details['selected'] = False
                studentsList.append(details)
            return studentsList
        return ["none"]

    @get(r'/api/lmn/sophomorixUsers/schooladmins((?P<user>/[a-z0-9\-_]*))?')
    @authorize('lm:users:schooladmins:read')
    @endpoint(api=True)
    def handle_api_sophomorix_schooladmins(self, http_context, user=None):
        """
        Get schooladmins list from LDAP tree.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param user: if provided, user to show (containing / at the beginning)
        :type user: str
        :return: List of schooladminss with details, one schooladmin per dict.
        :rtype: list of dict
        """

        schooladminsList = []
        if user is None:
            sophomorixCommand = ['sophomorix-query', '--schooladministrator', '--user-full', '-jj']
        else:
            sophomorixCommand = ['sophomorix-query', '--schooladministrator', '--user-full', '-jj', '--sam', user[1:]]
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        if 'USER' in result.keys():
            schooladmins = result['USER']
            for _, details in schooladmins.items():
                details['selected'] = False
                schooladminsList.append(details)
            return schooladminsList
        return ["none"]

    @get(r'/api/lmn/sophomorixUsers/globaladmins((?P<user>/[a-z0-9\-_]*))?')
    @authorize('lm:users:globaladmins:read')
    @endpoint(api=True)
    def handle_api_sophomorix_globaladmins(self, http_context, user=None):
        """
        Get globaladmins list from LDAP tree.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param user: if provided, user to show (containing / at the beginning)
        :type user: str
        :return: List of globaladminss with details, one globaladmin per dict.
        :rtype: list of dict
        """

        globaladminsList = []
        if user is None:
            sophomorixCommand = ['sophomorix-query', '--globaladministrator', '--user-full', '-jj']
        else:
            sophomorixCommand = ['sophomorix-query', '--globaladministrator', '--user-full', '-jj', '--sam', user[1:]]
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        if 'USER' in result.keys():
            globaladmins = result['USER']
            for _, details in globaladmins.items():
                details['selected'] = False
                globaladminsList.append(details)
            return globaladminsList
        return ["none"]

    @post(r'/api/lmn/sophomorixUsers/schooladmins')
    @authorize('lm:users:schooladmins:create')
    @endpoint(api=True)
    def handle_api_users_schooladmins_create(self, http_context):
        """
        Create school admins.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string
        """

        school = self.context.schoolmgr.school
        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        sophomorixCommand = ['sophomorix-admin', '--create-school-admin', user, '--school', school, '--random-passwd-save', '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        return result['COMMENT_EN']

    @post(r'/api/lmn/sophomorixUsers/(?P<user>[a-z0-9\-_]*)/comment')
    @authorize('lm:users:schooladmins:create')
    @endpoint(api=True)
    def handle_api_users_add_comment(self, http_context, user):
        """
        Add user comment.

        :param user: sAMAccountName to update
        :type user: basestring
        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string
        """

        school = self.context.schoolmgr.school
        comment = http_context.json_body()['comment']
        sophomorixCommand = ['sophomorix-user', '-u', user, '--school', school, '--comment', comment, '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        return result['COMMENT_EN']

    @patch(r'/api/lmn/sophomorixUsers/schooladmins')
    @authorize('lm:users:schooladmins:delete')
    @endpoint(api=True)
    def handle_api_users_schooladmins_delete(self, http_context):
        """
        Delete school admins.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string
        """

        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        sophomorixCommand = ['sophomorix-admin', '--kill', user, '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        return result['COMMENT_EN']

    @post(r'/api/lmn/sophomorixUsers/globaladmins')
    @authorize('lm:users:globaladmins:create')
    @endpoint(api=True)
    def handle_api_users_globaladmins_create(self, http_context):
        """
        Create global admins.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string
        """

        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        sophomorixCommand = ['sophomorix-admin', '--create-global-admin', user, '--random-passwd-save', '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        return result['COMMENT_EN']

    @patch(r'/api/lmn/sophomorixUsers/globaladmins')
    @authorize('lm:users:globaladmins:delete')
    @endpoint(api=True)
    def handle_api_users_globaladmins_delete(self, http_context):
        """
        Delete global admins.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string
        """

        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        sophomorixCommand = ['sophomorix-admin', '--kill', user, '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        return result['COMMENT_EN']

    @get(r'/api/lmn/sophomorixUsers/bindusers/(?P<level>.*)')
    @authorize('lm:users:globaladmins:create')
    @endpoint(api=True)
    def handle_api_users_binduser_get(self, http_context, level=''):
        """
        List school and global bindusers.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param level: school or global
        :type level: basestring
        :return: State of the command
        :rtype: string or list
        """

        secret_path = '/etc/linuxmuster/.secret/'

        binduser_list = []
        sophomorixCommand = ['sophomorix-query', f'--{level}binduser', '--user-full', '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        if 'USER' in result.keys():
            for username, details in result['USER'].items():
                if details['sophomorixRole'] == f"{level}binduser":
                    details['pw'] = False
                    if os.path.isfile(os.path.join(secret_path, username)):
                        details['pw'] = True
                    binduser_list.append(details)
            return binduser_list
        return []

    @post(r'/api/lmn/sophomorixUsers/bindusers/(?P<level>.*)')
    @authorize('lm:users:globaladmins:create')
    @endpoint(api=True)
    def handle_api_users_binduser_post(self, http_context, level=''):
        """
        Create school and global bindusers.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param level: school or global
        :type level: basestring
        :return: State of the command
        :rtype: string or list
        """

        binduser = http_context.json_body()['binduser']
        school_option = ''
        if level == 'school':
            school_option = ('--school', self.context.schoolmgr.school)
        sophomorixCommand = ['sophomorix-admin',
                             f'--create-{level}-binduser', binduser,
                             *school_option,
                             '--random-passwd-save', '-jj'
                             ]
        result = lmn_getSophomorixValue(sophomorixCommand, '')
        return result['COMMENT_EN']
