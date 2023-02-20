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

    @get(r'/api/lmn/groupmembership/groups')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_list_groups(self, http_context):
        """
        List all groups.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of groups or result for actions kill and create
        :rtype: dict or tuple
        """

        schoolname = self.context.schoolmgr.school
        username = self.context.identity
        user_details = AuthenticationService.get(self.context).get_provider().get_profile(username)
        isAdmin = "administrator" in user_details['sophomorixRole']

        membershipList = []
        usergroups = []
        if not isAdmin:
            # get groups specified user is member of
            for group in user_details['memberOf']:
                usergroups.append(group.split(',')[0].split('=')[1])

        # get all available classes and projects
        sophomorixCommand = ['sophomorix-query', '--class', '--project', '--schoolbase', schoolname, '--group-full', '-jj']
        groups = lmn_getSophomorixValue(sophomorixCommand, '')
        # get all available groups TODO

        # build membershipList with membership status
        for group in groups['LISTS']['GROUP']:
            membershipDict = {}
            groupDetails = groups['GROUP'][group]

            if group in usergroups or isAdmin or groupDetails['sophomorixHidden'] == "FALSE":
                membershipDict['groupname'] = group
                membershipDict['membership'] = group in usergroups or isAdmin
                membershipDict['admin'] = username in groupDetails['sophomorixAdmins'] or isAdmin
                membershipDict['joinable'] = groupDetails['sophomorixJoinable']
                membershipDict['DN'] = groupDetails['DN']
                membershipDict['members'] = groupDetails['sophomorixMembers']

                # Project name always starts with p_, but not classname
                if group[:2] == "p_":
                    membershipDict['type'] = 'project'
                    membershipDict['typename'] = 'Project'
                else:
                    membershipDict['type'] = 'schoolclass'
                    membershipDict['typename'] = 'Class'

                membershipList.append(membershipDict)

        #get printers
        sophomorixCommand = ['sophomorix-query', '--printergroup', '--schoolbase', schoolname, '-jj']
        printergroups = lmn_getSophomorixValue(sophomorixCommand, 'LISTS/GROUP')

        for printergroup in printergroups:
          if printergroup in usergroups or isAdmin:
            membershipList.append({'type': 'printergroup', 'typename': 'Printer', 'groupname': printergroup, 'membership': True})
          else:
            membershipList.append({'type': 'printergroup', 'typename': 'Printer', 'groupname': printergroup, 'membership': False})
        return membershipList, isAdmin, user_details

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
