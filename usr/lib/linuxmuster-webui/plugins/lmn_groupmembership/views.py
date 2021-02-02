"""
Tool to manage the groups (class, projects, printers ) in a linuxmuster
environment.
"""

# coding=utf-8
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/groupmembership/details')
    @authorize('lmn:groupmemberships:write')
    @endpoint(api=True)
    def handle_api_groupmembership_details(self, http_context):
        """
        Get the group informations of a specified group.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Group informations in LDAP ( name, owner, ... )
        :rtype: dict
        """

        action = http_context.json_body()['action']

        if http_context.method == 'POST':
            # schoolname = 'default-school'
            with authorize('lmn:groupmemberships:write'):
                if action == 'get-specified':
                    groupName = http_context.json_body()['groupName']
                    sophomorixCommand = ['sophomorix-query', '--group-members', '--group-full', '--sam', groupName, '-jj']
                    groupDetails = lmn_getSophomorixValue(sophomorixCommand, '')
                    if not 'MEMBERS' in groupDetails.keys():
                        groupDetails['MEMBERS'] = {}

            return groupDetails

    @url(r'/api/lmn/groupmembership')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_groups(self, http_context):
        """
        Performs diverses actions on groups, like list all groups, kill and create.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of groups or result for actions kill and create
        :rtype: dict or tuple
        """

        # TODO : this need to be splitted into atomic functions/tasks.

        schoolname = 'default-school'
        username = http_context.json_body()['username']
        action = http_context.json_body()['action']
        user_details = http_context.json_body()['profil']
        isAdmin = "administrator" in user_details['sophomorixRole']

        if http_context.method == 'POST':
            if action == 'list-groups':
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

            if action == 'kill-project':
                project = http_context.json_body()['project']
                sophomorixCommand = ['sophomorix-project', '-i', '-p', project, '-jj']
                groupAdmins = lmn_getSophomorixValue(sophomorixCommand, 'GROUPS/'+project+'/sophomorixAdmins')
                if username in groupAdmins or username == 'global-admin':
                    sophomorixCommand = ['sophomorix-project', '--kill', '-p', project, '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                    if result['TYPE'] == "ERROR":
                        return result['TYPE']['LOG']
                    # Try to return last result to frontend
                    return result['TYPE'], result['LOG']
                # TODO: This should be done by sophomorix
                return ['ERROR', 'Permission Denied']

            if action == 'create-project':
                ## Projectname must be in lowercase to avoid conflicts
                project = http_context.json_body()['project'].lower()
                sophomorixCommand = ['sophomorix-project',  '--admins', username, '--create', '-p', project, '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                if result['TYPE'] == "ERROR":
                    return result['TYPE']['LOG']
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
            entity = http_context.json_body()['entity']
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


    @url(r'/api/lm/search-project')
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
                elif objtype == 'usergroup':
                    sophomorixCommand = ['sophomorix-query', '--sam', login+'*', '--group-members', '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'MEMBERS')
                    if len(result) != 1:
                        return []
                    result = result[login]
                elif objtype == 'group':
                    sophomorixCommand = ['sophomorix-query', '--anyname', login+'*', '-jj']
                    return lmn_getSophomorixValue(sophomorixCommand, 'LISTS/GROUP')

                for _, details in result.items():
                    resultArray.append({
                            'label':details['sophomorixAdminClass'] + " " + details['sn'] + " " + details['givenName'],
                            'sn': details['sn'],
                            'givenName': details['givenName'],
                            'login': details['sAMAccountName'],
                            'sophomorixAdminClass': details['sophomorixAdminClass'],
                            })
            except:
                # Ignore SophomorixValue errors
                pass
            return resultArray
