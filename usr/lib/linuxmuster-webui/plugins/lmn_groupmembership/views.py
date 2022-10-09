"""
Tool to manage the groups (class, projects, printers ) in a linuxmuster
environment.
"""

# coding=utf-8
from jadi import component
from aj.api.http import url, get, post, delete, HttpPlugin
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

    @url(r'/api/lmn/changeGroup')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_set_group(self, http_context):
        """
        Handles join and hide options for a group.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Results of the operation
        :rtype: tuple
        """

        if http_context.method == 'POST':
            option  = http_context.json_body()['option']
            group = http_context.json_body()['group']
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

    @url(r'/api/lmn/groupmembership/membership')
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

        if http_context.method == 'POST':
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

    @url(r'/api/lmn/groupmembership/reset')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_reset(self, http_context):
        """Reset the admins of all projects or classes."""
        type = http_context.json_body()['type']
        all_groups = http_context.json_body()['all_groups']
        select = '-' + type[0] # -c for class and -p for project

        sophomorixCommand = ['sophomorix-'+type,  select, all_groups, '--admins', '""', '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
        if result['TYPE'] == "ERROR":
            return result['TYPE'], result['MESSAGE_EN']
        return result['TYPE'], result['LOG']

    @url(r'/api/lm/find-users')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_search_project(self, http_context):
        """
        Perform partial searchs in projects in the LDAP tree, per user or per
        group.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of search results
        :rtype: list
        """

        if http_context.method == 'POST':

            # Problem with unicode In&egraves --> In\xe8s (py) --> In\ufffds (replace)
            # Should be In&egraves --> Ines ( sophomorix supports this )
            # login = http_context.json_body()['login'].decode('utf-8', 'replace')

            login = http_context.json_body()['login']
            objtype = http_context.json_body()['type']
            resultArray = []

            try:
                if objtype == 'user':
                    sophomorixCommand = ['sophomorix-query', '--anyname', login+'*', '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'USER')
                elif objtype == 'teacher':
                    sophomorixCommand = ['sophomorix-query', '--anyname',
                                         login + '*', '--teacher', '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand,'USER')
                elif objtype == 'usergroup':
                    sophomorixCommand = ['sophomorix-query', '--sam', login+'*', '--group-members', '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'MEMBERS')
                    if len(result) != 1:
                        return []
                    result = result[login]
                elif objtype == 'group':
                    sophomorixCommand = ['sophomorix-query', '--anyname', login+'*', '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'LISTS')
                    return result['GROUP'] + result['ROOM']
                elif objtype == 'computer':
                    sophomorixCommand = ['sophomorix-query', '--sam', login+'*', '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'LISTS')
                    return result['COMPUTER']

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
