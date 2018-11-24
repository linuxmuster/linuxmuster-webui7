# coding=utf-8
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lm_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/groupmembership')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_settings(self, http_context):
        schoolname = 'default-school'
        username = http_context.json_body()['username']
        action = http_context.json_body()['action']

        if http_context.method == 'POST':
            if action == 'list-groups':
                membershipList = []

                # get groups specified user is member of
                sophomorixCommand = ['sophomorix-query',  '--schoolbase', schoolname, '--user-full', '-j', '--sam', username]
                groups = lmn_getSophomorixValue(sophomorixCommand, 'USER/'+username+'/memberOf')
                usergroups = []
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
                # get printers
                sophomorixCommand = ['sophomorix-query', '--project', '--schoolbase', schoolname, '-jj']
                projects = lmn_getSophomorixValue(sophomorixCommand, 'LISTS/GROUP')
                # build membershipList with membership status
                for project in projects:
                    if project in usergroups:
                        membershipList.append({'type': 'project', 'groupname': project, 'icon': 'fa fa-flask', 'changed': False, 'membership': True})
                    else:
                        membershipList.append({'type': 'project', 'groupname': project, 'icon': 'fa fa-flask', 'changed': False, 'membership': False})
                for schoolclass in schoolclasses:
                    if schoolclass in usergroups:
                        membershipList.append({'type': 'schoolclass', 'groupname': schoolclass, 'icon': 'fa fa-users', 'changed': False, 'membership': True})
                    else:
                        membershipList.append({'type': 'schoolclass', 'groupname': schoolclass, 'icon': 'fa fa-users', 'changed': False, 'membership': False})
                for printergroup in printergroups:
                    if printergroup in usergroups:
                        membershipList.append({'type': 'printergroup', 'groupname': printergroup, 'icon': 'fa fa-fw fa-print', 'changed': False, 'membership': True})
                    else:
                        membershipList.append({'type': 'printergroup', 'groupname': printergroup, 'icon': 'fa fa-fw fa-print', 'changed': False, 'membership': False})
                return membershipList

            if action == 'create-project':
                project = http_context.json_body()['project']
                sophomorixCommand = ['sophomorix-project',  '--admins', username, '--create', '-p', project , '-jj']
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
                for group in groups:
                    # Temporary removed because changed attribute is set wrong
                    #if group['changed'] is False:
                    #    continue
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
                # Try to return last result to frontend
                try:
                    return result['TYPE'], result['LOG']
                # If nothing changed result is empty so return 0
                except NameError:
                    return 0
