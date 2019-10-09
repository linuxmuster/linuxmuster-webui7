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
                    membergroups = ",".join(http_context.json_body()['membergroups'])
                    admingroups = ",".join(http_context.json_body()['admingroups'])

                    admins = ",".join(http_context.json_body()['admins'])

                    user_details = lmn_user_details(username)
                    isAdmin = "administrator" in user_details['sophomorixRole']

                    sophomorixCommand = ['sophomorix-project', '-i', '-p', groupName, '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'GROUPS/'+groupName)
                    groupAdmins = result['sophomorixAdmins']
                    groupAdmingroups = result['sophomorixAdminGroups']
                    membersToAdd = []
                    membersToRemove = []
                    if username in groupAdmins or isAdmin or user_details['sophomorixAdminClass'] in groupAdmingroups:
                        for user, details in members.iteritems():
                                if details['membership'] is True:
                                    membersToAdd.append(user)
                                else:
                                    membersToRemove.append(user)

                        membersToAddCSV = ",".join(membersToAdd)
                        membersToRemoveCSV = ",".join(membersToRemove)
                        sophomorixCommand = ['sophomorix-project', '-p', groupName,
                                             '--addmembers', membersToAddCSV,
                                             '--removemembers', membersToRemoveCSV,
                                             '--admins', admins,
                                             '--admingroups', admingroups,
                                             '--membergroups', membergroups,
                                             '-jj']
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

                if action == 'get-students':
                    dn = http_context.json_body()['dn']
                    sophomorixCommand = ['sophomorix-query', '--group-members', '--class', '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'MEMBERS')
                    classes = []
                    students_per_class = {cl:[] for cl in result.keys()}
                    students = {}
                    for cl,student in result.iteritems():
                        classes.append({'name':cl,'isVisible':0})
                        for login,details in student.iteritems():
                            if details['sophomorixRole'] == 'student':
                                students_per_class[cl].append(details)
                                details['membership'] = dn in details['memberOf']
                                students[login] = details

                    return students_per_class, classes, students

            return groupDetails

    @url(r'/api/lmn/groupmembership')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_groups(self, http_context):
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
                        membershipDict['changed'] = False
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

                ## DEPRECATED ???
                # get printers
                # sophomorixCommand = ['sophomorix-query', '--printergroup', '--schoolbase', schoolname, '-jj']
                # printergroups = lmn_getSophomorixValue(sophomorixCommand, 'LISTS/GROUP')

                # for printergroup in printergroups:
                    # if printergroup in usergroups or isAdmin:
                        # membershipList.append({'type': 'printergroup', 'typename': 'Printer', 'groupname': printergroup, 'changed': False, 'membership': True})
                    # else:
                        # membershipList.append({'type': 'printergroup', 'typename': 'Printer', 'groupname': printergroup, 'changed': False, 'membership': False})
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

    @url(r'/api/lmn/changeGroup')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_set_group(self, http_context):
        """Handles join and hide options for a group."""
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
            else:
                return result['TYPE'], result['LOG']
