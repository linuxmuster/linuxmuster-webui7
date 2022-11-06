"""
APIs for user management in linuxmuster.net. Basically parse the output of
sophomorix commands.
"""

import unicodecsv as csv
import os
import subprocess
import magic
import io

from jadi import component
from aj.api.http import get, post, url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import lmn_getSophomorixValue
from aj.plugins.lmn_common.lmnfile import LMNFile


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

    @url(r'/api/lm/sophomorixUsers/teachers')
    @endpoint(api=True)
    def handle_api_sophomorix_teachers(self, http_context):
        """
        Get teachers list from LDAP tree.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of teachers with details, one teacher per dict.
        :rtype: list of dict
        """

        action = http_context.json_body()['action']
        if http_context.method == 'POST':
            schoolname = self.context.schoolmgr.school
            teachersList = []

            if action == 'get-all':
                with authorize('lm:users:teachers:read'):
                    # TODO: This could run with --user-basic but not all memberOf are filled. Needs verification
                    sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-full', '-jj']
            else:
                with authorize('lm:users:teachers:read'):
                    user = http_context.json_body()['user']
                    sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-full', '-jj', '--sam', user]
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

    @url(r'/api/lm/sophomorixUsers/students')
    @endpoint(api=True)
    def handle_api_sophomorix_students(self, http_context):
        """
        Get students list from LDAP tree.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of students with details, one student per dict.
        :rtype: list of dict
        """

        action = http_context.json_body()['action']
        if http_context.method == 'POST':
            schoolname = self.context.schoolmgr.school

            studentsList = []
            with authorize('lm:users:students:read'):
                if action == 'get-all':
                    sophomorixCommand = ['sophomorix-query', '--student', '--schoolbase', schoolname, '--user-full', '-jj']
                else:
                    user = http_context.json_body()['user']
                    # sophomorixCommand = ['sophomorix-query', '--student', '--schoolbase', schoolname, '--user-full', '-jj', '--sam', user]
                    sophomorixCommand = ['sophomorix-query', '--user-full', '-jj', '--sam', user]
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

    @url(r'/api/lm/sophomorixUsers/schooladmins')
    @endpoint(api=True)
    def handle_api_sophomorix_schooladmins(self, http_context):
        """
        Get schooladmins list from LDAP tree.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of schooladminss with details, one schooladmin per dict.
        :rtype: list of dict
        """

        if http_context.method == 'POST':
            action = http_context.json_body()['action']
            schooladminsList = []
            with authorize('lm:users:schooladmins:read'):
                if action == 'get-all':
                    sophomorixCommand = ['sophomorix-query', '--schooladministrator', '--user-full', '-jj']
                else:
                    user = http_context.json_body()['user']
                    sophomorixCommand = ['sophomorix-query', '--schooladministrator', '--user-full', '-jj', '--sam', user]
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                if 'USER' in result.keys():
                    schooladmins = result['USER']
                    for _, details in schooladmins.items():
                        details['selected'] = False
                        schooladminsList.append(details)
                    return schooladminsList
                return ["none"]

    @url(r'/api/lm/sophomorixUsers/globaladmins')
    @endpoint(api=True)
    def handle_api_sophomorix_globaladmins(self, http_context):
        """
        Get globaladmins list from LDAP tree.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of globaladminss with details, one globaladmin per dict.
        :rtype: list of dict
        """

        if http_context.method == 'POST':
            action = http_context.json_body()['action']
            globaladminsList = []
            with authorize('lm:users:globaladmins:read'):
                if action == 'get-all':
                    sophomorixCommand = ['sophomorix-query', '--globaladministrator', '--user-full', '-jj']
                else:
                    user = http_context.json_body()['user']
                    sophomorixCommand = ['sophomorix-query', '--globaladministrator', '--user-full', '-jj', '--sam', user]
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                if 'USER' in result.keys():
                    globaladmins = result['USER']
                    for _, details in globaladmins.items():
                        details['selected'] = False
                        globaladminsList.append(details)
                    return globaladminsList
                return ["none"]

    @url(r'/api/lm/users/change-school-admin')
    @authorize('lm:users:schooladmins:create')
    @endpoint(api=True)
    def handle_api_users_schooladmins_create(self, http_context):
        """
        Create or delete school admins.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string
        """
        school = self.context.schoolmgr.school
        action = http_context.json_body()['action']
        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        if action == 'create':
            with authorize('lm:users:schooladmins:create'):
                sophomorixCommand = ['sophomorix-admin', '--create-school-admin', user, '--school', school, '--random-passwd-save', '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                #if result['TYPE'] == "ERROR":
                #    return ["ERROR", result['MESSAGE_EN']]
                #if result['TYPE'] == "LOG":
                #    return ["LOG", result['LOG']]
                return result['COMMENT_EN']
                ### return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'delete':
            with authorize('lm:users:schooladmins:delete'):
                sophomorixCommand = ['sophomorix-admin', '--kill', user, '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                #if result['TYPE'] == "ERROR":
                #    return ["ERROR", result['MESSAGE_EN']]
                #if result['TYPE'] == "LOG":
                #    return ["LOG", result['LOG']]
                return result['COMMENT_EN']

    @url(r'/api/lm/users/change-global-admin')
    @authorize('lm:users:globaladmins:create')
    @endpoint(api=True)
    def handle_api_users_globaladmins_create(self, http_context):
        """
        Create or delete global admins.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string
        """

        action = http_context.json_body()['action']
        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        if action == 'create':
            with authorize('lm:users:globaladmins:create'):
                sophomorixCommand = ['sophomorix-admin', '--create-global-admin', user, '--random-passwd-save', '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                #if result['TYPE'] == "ERROR":
                #    return ["ERROR", result['MESSAGE_EN']]
                #if result['TYPE'] == "LOG":
                #    return ["LOG", result['LOG']]
                return result['COMMENT_EN']
                # return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'delete':
            with authorize('lm:users:globaladmins:delete'):
                sophomorixCommand = ['sophomorix-admin', '--kill', user, '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                #if result['TYPE'] == "ERROR":
                #    return result['MESSAGE_EN']
                #if result['TYPE'] == "LOG":
                #    return result['LOG']
                return result['COMMENT_EN']
                # return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')

    @url(r'/api/lm/users/binduser/(?P<level>.*)')
    @authorize('lm:users:globaladmins:create')
    @endpoint(api=True)
    def handle_api_users_binduser(self, http_context, level=''):
        """
        List or create school and global bindusers.
        Method POST and GET

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param level: school or global
        :type level: basestring
        :return: State of the command
        :rtype: string or list
        """

        secret_path = '/etc/linuxmuster/.secret/'

        if http_context.method == 'GET':
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

        if http_context.method == 'POST':
            binduser = http_context.json_body()['binduser']
            # level may be global or school
            level = http_context.json_body()['level']
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

    @url(r'/api/lm/users/get-group-quota')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_group_quota(self, http_context):
        """
        Get samba share limits for a group list. Prepare type key for style
        (danger, warning, success) to display status.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            groupList = http_context.json_body()['groupList']
            sophomorixCommand = ['sophomorix-quota', '--smbcquotas-only', '-i', '--user', ','.join(groupList), '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'QUOTA/USERS')

            quotaMap = {}
            school = self.context.schoolmgr.school
            # Only read default-school for the moment, must be maybe adapted later
            for user in groupList:
                share = result[user]["SHARES"][school]['smbcquotas']
                if int(share['HARDLIMIT_MiB']) == share['HARDLIMIT_MiB']:
                    # Avoid strings for non set quotas
                    used = int(float(share['USED_MiB']) / share['HARDLIMIT_MiB'] * 100)
                    soft = int(float(share['SOFTLIMIT_MiB']) / share['HARDLIMIT_MiB'] * 100)
                    if used >= 80:
                        state = "danger"
                    elif used >= 60:
                        state = "warning"
                    else:
                        state = "success"

                    quotaMap[user] = {
                        "USED": used,
                        "SOFTLIMIT": soft,
                        "TYPE": state,
                    }
                else:
                    quotaMap[user] = {
                        "USED": 0,
                        "SOFTLIMIT": 0,
                        "TYPE": "success",
                    }
            return quotaMap


