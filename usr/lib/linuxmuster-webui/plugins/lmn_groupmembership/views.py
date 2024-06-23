"""
Tool to manage the groups (class, projects, printers ) in a linuxmuster
environment.
"""

# coding=utf-8
from jadi import component

from aj.api.http import get, post, delete, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/groupmembership/projects')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_list_projects(self, http_context):
        """
        List all projects visible for the current user.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of projects
        :rtype: list
        """

        username = self.context.identity
        user_profile = AuthenticationService.get(self.context).get_provider().get_profile(username)

        projects = self.context.ldapreader.schoolget('/projects', dict=False)
        user_projects = []

        for project in projects:
            member = project.cn in user_profile['projects'] or user_profile['isAdmin']

            if member or not project.sophomorixHidden:
                project.get_all_members()
                projectDict = project.asdict()

                projectDict['groupname'] = project.cn
                projectDict['membership'] = member
                projectDict['admin'] = username in project.sophomorixAdmins or user_profile['isAdmin']
                projectDict['members'] = project.sophomorixMembers
                projectDict['type'] = 'project'

                user_projects.append(projectDict)

        return user_projects

    @get(r'/api/lmn/groupmembership/printers')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_list_printers(self, http_context):
        """
        List all printers.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of printers
        :rtype: list
        """

        username = self.context.identity
        user_profile = AuthenticationService.get(self.context).get_provider().get_profile(username)
        printers = self.context.ldapreader.schoolget('/printers')

        for printer in printers:
            printer['type'] = 'printergroup'
            printer['groupname'] = printer['cn']
            printer['membership'] = printer['cn'] in user_profile['printers'] or user_profile['isAdmin']

        return printers

    @get(r'/api/lmn/groupmembership/schoolclasses')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_list_groups(self, http_context):
        """
        List all schoolclasses and the current user's membership.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of schoolclasses
        :rtype: dict or tuple
        """

        username = self.context.identity
        user_profile = AuthenticationService.get(self.context).get_provider().get_profile(username)

        schoolclasses = self.context.ldapreader.schoolget('/schoolclasses')

        for schoolclass in schoolclasses:
            member = schoolclass['cn'] in user_profile['schoolclasses'] or user_profile['isAdmin']

            if member or not schoolclass['sophomorixHidden']:
                schoolclass['groupname'] = schoolclass['cn']
                schoolclass['membership'] = member
                schoolclass['admin'] = username in schoolclass['sophomorixAdmins'] or user_profile['isAdmin']
                schoolclass['members'] = schoolclass['sophomorixMembers']
                schoolclass['type'] = 'schoolclass'

        return schoolclasses

    @get(r'/api/lmn/groupmembership/groups/(?P<groupName>.+)')
    @authorize('lmn:groupmemberships:write')
    @endpoint(api=True)
    def handle_api_groupmembership_details(self, http_context, groupName=''):
        """
        Get the group informations of a specified group.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Group informations in LDAP ( name, owner, ... )
        :rtype: dict
        """

        sophomorixCommand = ['sophomorix-query', '--group-members', '--group-full', '--sam', groupName, '-jj']
        groupDetails = lmn_getSophomorixValue(sophomorixCommand, '')
        if not 'MEMBERS' in groupDetails.keys():
            groupDetails['MEMBERS'] = {}

        return groupDetails

    @delete(r'/api/lmn/groupmembership/projects/(?P<project>.+)')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_kill_project(self, http_context, project=''):
        """
        Kill specified project.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of groups or result for actions kill and create
        :rtype: dict or tuple
        """

        username = self.context.identity
        user_details = AuthenticationService.get(self.context).get_provider().get_profile(username)

        sophomorixCommand = ['sophomorix-project', '-i', '-p', project, '-jj']
        groupAdmins = lmn_getSophomorixValue(sophomorixCommand, f'GROUPS/{project}/sophomorixAdmins')

        if username in groupAdmins or user_details['sophomorixRole'] in ['globaladministrator', 'schooladministrator']:
            sophomorixCommand = ['sophomorix-project', '--kill', '-p', project, '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
            if result['TYPE'] == "ERROR":
                return result['TYPE']['LOG']
            # Try to return last result to frontend
            return result['TYPE'], result['LOG']
        # TODO: This should be done by sophomorix
        return ['ERROR', 'Permission Denied']

    @post(r'/api/lmn/groupmembership/projects/(?P<project>.+)')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_create_project(self, http_context, project=''):
        """
        Create a project.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of groups or result for actions kill and create
        :rtype: dict or tuple
        """

        schoolname = self.context.schoolmgr.school
        username = self.context.identity

        ## Projectname must be in lowercase to avoid conflicts
        sophomorixCommand = ['sophomorix-project',  '--admins', username, '--create', '-p', project.lower(), '--school', schoolname, '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
        if result['TYPE'] == "ERROR":
            return result['TYPE'],result['MESSAGE_EN']
        return result['TYPE'], result['LOG']

    @post(r'/api/lmn/groupmembership/groupoptions/(?P<group>.+)')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_set_group(self, http_context, group=''):
        """
        Handles join, hide, maillist options for a group.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Results of the operation
        :rtype: tuple
        """

        option  = http_context.json_body()['option']
        groupType = http_context.json_body()['type']

        if groupType == "project":
            sophomorixCommand = ['sophomorix-project',  option, '--project', group, '-jj']
        else:
            # Class
            sophomorixCommand = ['sophomorix-class',  option, '--class', group, '-jj']

        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')

        if result['TYPE'] == "ERROR":
            return result['TYPE'], result['MESSAGE_EN']
        return result['TYPE'], result['LOG']

    @post(r'/api/lmn/groupmembership/membership')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_set_members(self, http_context):
        """
        Manages the members of a project (add, remove, ...).
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Result of the operation
        :rtype: tuple
        """

        # TODO : missing body in delete request method to do it properly ...

        action  = http_context.json_body()['action']
        groupname = http_context.json_body()['groupname']
        entity = http_context.json_body()['entity'].strip(",")
        try:
            objtype = http_context.json_body()['type']
        except KeyError:
            objtype = 'project'

        possible_actions = [
            'removemembers',
            'addmembers',
            'addadmins',
            'removeadmins',
            'addmembergroups',
            'removemembergroups',
            'addadmingroups',
            'removeadmingroups',

        ]

        if action in possible_actions:
            sophomorixCommand = ['sophomorix-'+objtype,  '--'+action, entity, '--'+objtype, groupname, '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
            if result['TYPE'] == "ERROR":
                return result['TYPE'], result['MESSAGE_EN']
            return result['TYPE'], result['LOG']

    @post(r'/api/lmn/groupmembership/resetadmins')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_reset(self, http_context):
        """Reset the admins of all projects or classes."""

        type = http_context.json_body()['type']
        all_groups = http_context.json_body()['all_groups']
        select = f'-{type[0]}'  # -c for class and -p for project

        sophomorixCommand = [f'sophomorix-{type}',  select, all_groups, '--admins', '""', '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
        if result['TYPE'] == "ERROR":
            return result['TYPE'], result['MESSAGE_EN']
        return result['TYPE'], result['LOG']

    # TODO : Duplicate with ldap-search in lmn_quotas ?

    @post(r'/api/lmn/find/user')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_find_user(self, http_context):
        """
        Search for an user.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of search results
        :rtype: list
        """

        # TODO : should be get request, but passing the name in the url
        # gives some encoding problems

        # Problem with unicode In&egraves --> In\xe8s (py) --> In\ufffds (replace)
        # Should be In&egraves --> Ines ( sophomorix supports this )
        # login = http_context.json_body()['login'].decode('utf-8', 'replace')

        resultArray = []
        name = http_context.json_body()['name']

        try:
            sophomorixCommand = ['sophomorix-query', '--anyname', f'{name}*', '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'USER')

            for _, details in result.items():
                resultArray.append({
                        'label': f"{details['sophomorixAdminClass']} {details['sn']} {details['givenName']}",
                        'sn': details['sn'],
                        'givenName': details['givenName'],
                        'login': details['sAMAccountName'],
                        'sophomorixAdminClass': details['sophomorixAdminClass'],
                        'sophomorixRole': details.get('sophomorixRole', ''),
                        })
        except:
            # Ignore SophomorixValue errors
            pass
        return resultArray

    @get(r'/api/lmn/find/teacher/(?P<login>.+)')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_find_teacher(self, http_context, login):
        """
        Search for an teacher.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of search results
        :rtype: list
        """

        resultArray = []

        try:
            sophomorixCommand = ['sophomorix-query', '--anyname', f'{login}*', '--teacher', '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand,'USER')

            for _, details in result.items():
                resultArray.append({
                        'label': f"{details['sophomorixAdminClass']} {details['sn']} {details['givenName']}",
                        'sn': details['sn'],
                        'givenName': details['givenName'],
                        'login': details['sAMAccountName'],
                        'sophomorixAdminClass': details['sophomorixAdminClass'],
                        'sophomorixRole': details.get('sophomorixRole', ''),
                        })
        except:
            # Ignore SophomorixValue errors
            pass
        return resultArray

    @get(r'/api/lmn/find/usergroup/(?P<group>.+)')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_find_usergroup(self, http_context, group):
        """
        Search for members in a group

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of search results
        :rtype: list
        """

        resultArray = []

        try:
            sophomorixCommand = ['sophomorix-query', '--sam', f'{group}*', '--group-members', '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'MEMBERS')

            for classe in result.keys():
                for _, details in result[classe].items():
                    resultArray.append({
                            'label': f"{details['sophomorixAdminClass']} {details['sn']} {details['givenName']}",
                            'sn': details['sn'],
                            'givenName': details['givenName'],
                            'login': details['sAMAccountName'],
                            'sophomorixAdminClass': details['sophomorixAdminClass'],
                            'sophomorixRole': details.get('sophomorixRole', ''),
                            })
        except:
            # Ignore SophomorixValue errors
            pass
        return resultArray

    @get(r'/api/lmn/find/group/(?P<group>.+)')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_find_group(self, http_context, group):
        """
        Search for members in a group

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of search results
        :rtype: list
        """

        resultArray = []

        try:
            sophomorixCommand = ['sophomorix-query', '--anyname', f'{group}*', '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'LISTS')
            return result['GROUP'] + result['ROOM']

        except:
            # Ignore SophomorixValue errors
            pass
        return resultArray

    @delete(r'/api/lmn/groupmembership/schoolclass/(?P<schoolclass>.+)')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_kill_schoolclass(self, http_context, schoolclass=''):
        """
        Kill specified schoolclass.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of groups or result for actions kill and create
        :rtype: dict or tuple
        """

        username = self.context.identity
        user_details = AuthenticationService.get(self.context).get_provider().get_profile(username)
        isAdmin = "administrator" in user_details['sophomorixRole']

        if isAdmin:
            sophomorixCommand = ['sophomorix-class', '--kill', '--class', schoolclass, '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
            if result['TYPE'] == "ERROR":
                return ['ERROR', result['MESSAGE_EN']]
            # Try to return last result to frontend
            return result['TYPE'], result['LOG']
        # TODO: This should be done by sophomorix
        return ['ERROR', 'Permission Denied']

    @get(r'/api/lmn/find/computer/(?P<computer>.+)')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_find_computer(self, http_context, computer):
        """
        Search for computers.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of search results
        :rtype: list
        """

        resultArray = []

        try:
            sophomorixCommand = ['sophomorix-query', '--sam', f'{computer}*', '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'LISTS')
            return result['COMPUTER']

        except:
            # Ignore SophomorixValue errors
            pass
        return resultArray
