# coding=utf-8
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_getSophomorixValue, lmn_user_details


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/groupmembership/details')
    @authorize('lmn:groupmemberships:write')
    @endpoint(api=True)
    def handle_api_groupmembership_details(self, http_context):
        action = http_context.json_body()['action']
        if http_context.method == 'POST':
            schoolname = 'default-school'
            with authorize('lmn:groupmemberships:write'):
                if action == 'set-members':
                    members = http_context.json_body()['members']
                    groupName = http_context.json_body()['groupName']
                    username = http_context.json_body()['username']
                    admins = ",".join(http_context.json_body()['admins'])

                    user_details = lmn_user_details(username)
                    isAdmin = "administrator" in user_details['sophomorixRole']

                    sophomorixCommand = ['sophomorix-project', '-i', '-p', groupName, '-jj']
                    groupAdmins = lmn_getSophomorixValue(sophomorixCommand, 'GROUPS/'+groupName+'/sophomorixAdmins')
                    membersToAdd = []
                    membersToRemove = []
                    if username in groupAdmins or isAdmin:
                        i = 0
                        for member in members:
                            if members[i]['membership'] is True:
                                membersToAdd.append(members[i]['sAMAccountName'])
                            else:
                                membersToRemove.append(members[i]['sAMAccountName'])
                            i = i + 1
                        membersToAddCSV = ",".join(membersToAdd)
                        membersToRemoveCSV = ",".join(membersToRemove)
                        sophomorixCommand = ['sophomorix-project', '-p', groupName, '--addmembers', membersToAddCSV, '--removemembers', membersToRemoveCSV, '--admins', admins,'-jj']
                        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                        if result['TYPE'] == "ERROR":
                            return result['TYPE']['LOG']
                        # Try to return last result to frontend
                        else:
                            return result['TYPE'], result['LOG']
                    else:
                        # TODO: This should be done by sophomorix
                        return ['ERROR', 'Permission Denied']

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
        schoolname = 'default-school'
        username = http_context.json_body()['username']
        action = http_context.json_body()['action']
        user_details = lmn_user_details(username)
        isAdmin = "administrator" in user_details['sophomorixRole']

        if http_context.method == 'POST':
            if action == 'list-groups':
                membershipList = []
                usergroups = []
                if not isAdmin:
                    # get groups specified user is member of
                    sophomorixCommand = ['sophomorix-query',  '--schoolbase', schoolname, '--user-full', '-jj', '--sam', username]
                    groups = lmn_getSophomorixValue(sophomorixCommand, 'USER/'+username+'/memberOf')

                    for group in groups:
                        usergroups.append(group.split(',')[0].split('=')[1])

                # get all available classes
                # get classes
                sophomorixCommand = ['sophomorix-query', '--class', '--schoolbase', schoolname, '--group-full', '-jj']
                schoolclasses = lmn_getSophomorixValue(sophomorixCommand, 'LISTS/GROUP')
                # get all available groups
                # get printers
                sophomorixCommand = ['sophomorix-query', '--printergroup', '--schoolbase', schoolname, '-jj']
                printergroups = lmn_getSophomorixValue(sophomorixCommand, 'LISTS/GROUP')
                # get projects
                sophomorixCommand = ['sophomorix-query', '--project', '--group-full', '--schoolbase', schoolname, '-jj']
                # Check if there are any project if not return empty list
                projects_raw = lmn_getSophomorixValue(sophomorixCommand, '')
                if 'GROUP' not in projects_raw:
                    projects = []
                else:
                    projects = projects_raw['GROUP']
                # build membershipList with membership status
                for project in projects:
                    if project in usergroups or isAdmin:
                        if username in projects[project]['sophomorixAdmins'] or isAdmin:
                            membershipList.append({'type': 'project', 'typename': 'Project', 'groupname': project, 'changed': False, 'membership': True, 'admin': True, 'joinable': projects[project]['sophomorixJoinable']})
                        else:
                            membershipList.append({'type': 'project', 'typename': 'Project', 'groupname': project, 'changed': False, 'membership': True, 'admin': False, 'joinable': projects[project]['sophomorixJoinable']})
                    elif projects[project]['sophomorixHidden'] == "FALSE":
                        membershipList.append({'type': 'project', 'typename': 'Project', 'groupname': project, 'changed': False, 'membership': False, 'admin': False, 'joinable': projects[project]['sophomorixJoinable']})
                for schoolclass in schoolclasses:
                    if schoolclass in usergroups or isAdmin:
                        membershipList.append({'type': 'schoolclass', 'typename': 'Class', 'groupname': schoolclass, 'changed': False, 'membership': True})
                    else:
                        membershipList.append({'type': 'schoolclass', 'typename': 'Class', 'groupname': schoolclass, 'changed': False, 'membership': False})
                for printergroup in printergroups:
                    if printergroup in usergroups or isAdmin:
                        membershipList.append({'type': 'printergroup', 'typename': 'Printer', 'groupname': printergroup, 'changed': False, 'membership': True})
                    else:
                        membershipList.append({'type': 'printergroup', 'typename': 'Printer', 'groupname': printergroup, 'changed': False, 'membership': False})
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
                    else:
                        return result['TYPE'], result['LOG']
                else:
                    # TODO: This should be done by sophomorix
                    return ['ERROR', 'Permission Denied']

                sophomorixCommand = ['sophomorix-project',  '--admins', username, '--create', '-p', project, '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                if result['TYPE'] == "ERROR":
                    return result['TYPE']['LOG']
                else:
                    return result['TYPE'], result['LOG']

            if action == 'create-project':
                ## Projectname must be in lowercase to avoid conflicts
                project = http_context.json_body()['project'].lower()
                sophomorixCommand = ['sophomorix-project',  '--admins', username, '--create', '-p', project, '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                if result['TYPE'] == "ERROR":
                    return result['TYPE']['LOG']
                else:
                    return result['TYPE'], result['LOG']

            if action == 'set-groups':
                groups = http_context.json_body()['groups']
                schoolclassToAdd = ''
                schoolclassToRemove = ''
                printergroupToAdd = ''
                printergroupToRemove = ''
                projectToAdd = []
                projectToRemove = []
                for group in groups:
                    # TODO
                    # Temporary removed because changed attribute is set wrong
                    if group['changed'] is False:
                        continue

                    # schoolclasses
                    if group['type'] == 'schoolclass':
                        if group['membership'] is True:
                            schoolclassToAdd += group['groupname']+','
                        if group['membership'] is False:
                            schoolclassToRemove += group['groupname']+','
                    # printergroups
                    if group['type'] == 'printergroup':
                        if group['membership'] is True:
                            printergroupToAdd += group['groupname']+','
                        if group['membership'] is False:
                            printergroupToRemove += group['groupname']+','
                    # projects
                    if group['type'] == 'project':
                        if group['membership'] is True:
                            projectToAdd.append(group['groupname'])
                        if group['membership'] is False:
                            projectToRemove.append(group['groupname'])
                if schoolclassToAdd:
                    sophomorixCommand = ['sophomorix-class',  '--addadmins', username, '--class', schoolclassToAdd, '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                    if result['TYPE'] == "ERROR":
                        return result['TYPE']['LOG']
                if schoolclassToRemove:
                    sophomorixCommand = ['sophomorix-class',  '--removeadmins', username, '--class', schoolclassToRemove, '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                    if result['TYPE'] == "ERROR":
                        return result['TYPE']['LOG']
                if printergroupToAdd:
                    sophomorixCommand = ['sophomorix-group',  '--addmembers', username, '--group', printergroupToAdd, '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                    if result['TYPE'] == "ERROR":
                        return result['TYPE'], result['MESSAGE_EN']
                if printergroupToRemove:
                    sophomorixCommand = ['sophomorix-group',  '--removemembers', username, '--group', printergroupToRemove, '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                    if result['TYPE'] == "ERROR":
                        return result['TYPE']['LOG']
                if projectToAdd:
                    for project in projectToAdd:
                        sophomorixCommand = ['sophomorix-project',  '--addadmins', username, '--project', project, '-jj']
                        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                        if result['TYPE'] == "ERROR":
                            return result['TYPE'], result['MESSAGE_EN']
                if projectToRemove:
                    for project in projectToRemove:
                        sophomorixCommand = ['sophomorix-project',  '--removeadmins', username, '--project', project, '-jj']
                        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                        if result['TYPE'] == "ERROR":
                            return result['TYPE']['LOG']
                # Try to return last result to frontend
                try:
                    return result['TYPE'], result['LOG']
                # If nothing changed result is empty so return 0
                except NameError:
                    return 0

    @url(r'/api/lmn/changeProject')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_set_project(self, http_context):
        """Handles join and hide options for a project."""
        if http_context.method == 'POST':
            option  = http_context.json_body()['option']
            project = http_context.json_body()['project']
            sophomorixCommand = ['sophomorix-project',  option, '--project', project, '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
            if result['TYPE'] == "ERROR":
                return result['TYPE'], result['MESSAGE_EN']
            else:
                return result['TYPE'], result['LOG']
