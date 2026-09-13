"""
Tool to manage the groups (class, projects, printers ) in a linuxmuster
environment.
"""

# coding=utf-8
import os
from jadi import component
from urllib.parse import quote, unquote

from aj.api.http import get, post, delete, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import lmn_getSophomorixValue, LMNAPI_UNAVAILABLE_MESSAGE
from aj.plugins.lmn_common import lmnapi_client
from aj.plugins.lmn_common.tools import sort_schoolclasses
from linuxmusterTools.ldapconnector import LMNPrinter, LMNProject, LMNSchoolclass


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
        user_profile = self.context.profile

        projects = self.context.ldapreader.schoolget('/projects', as_dict=False)
        user_projects = []

        for project in projects:
            member = user_profile['dn'] in project.member or username in project.sophomorixAdmins

            if member or not project.sophomorixHidden:
                projectDict = project.as_dict()

                projectDict['groupname'] = project.cn
                projectDict['membership'] = member
                projectDict['admin'] = username in project.sophomorixAdmins or user_profile['isAdmin']
                projectDict['members'] = project.sophomorixMembers
                projectDict['type'] = 'project'
                projectDict['no_admin'] = len(project.sophomorixAdmins + project.sophomorixAdminGroups) == 0
                projectDict['no_member'] = len(project.sophomorixMembers + project.sophomorixMemberGroups) == 0

                user_projects.append(projectDict)

        return user_projects

    @get(r'/api/lmn/groupmembership/all_members_project/(?P<project>.+)')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_get_all_members_projects(self, http_context, project=''):
        """
        Get all members of a given project.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Project data
        :rtype: dict
        """

        projectName = unquote(project.encode('latin-1'))
        project = self.context.ldapreader.schoolget(f'/projects/{projectName}', as_dict=False)

        project.get_all_members()
        projectDict = project.as_dict()

        return projectDict

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

        user_profile = self.context.profile
        printers = self.context.ldapreader.schoolget('/printers')

        for printer in printers:
            printer['type'] = 'printergroup'
            printer['groupname'] = printer['cn']
            printer['membership'] = user_profile['dn'] in printer['member']
            printer['admin'] = user_profile['isAdmin']

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
        user_profile = self.context.profile

        schoolclasses = self.context.ldapreader.schoolget('/schoolclasses')
        to_remove = []

        for schoolclass in schoolclasses:
            member = user_profile['dn'] in schoolclass['member']

            if member or not schoolclass['sophomorixHidden']:
                schoolclass['groupname'] = schoolclass['cn']
                schoolclass['membership'] = member
                schoolclass['admin'] = username in schoolclass['sophomorixAdmins'] or user_profile['isAdmin']
                schoolclass['members'] = schoolclass['sophomorixMembers']
                schoolclass['type'] = 'schoolclass'
            else:
                to_remove.append(schoolclass)

        for schoolclass in to_remove:
            schoolclasses.remove(schoolclass)

        return sort_schoolclasses(schoolclasses)

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

        group = unquote(groupName.encode('latin-1'))
        sophomorixCommand = ['sophomorix-query', '--group-members', '--group-full', '--sam', group, '-jj']
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

        projectName = unquote(project.encode('latin-1'))
        sophomorixCommand = ['sophomorix-project', '-i', '-p', projectName, '-jj']
        groupAdmins = lmn_getSophomorixValue(sophomorixCommand, f'GROUPS/{projectName}/sophomorixAdmins')

        if username in groupAdmins or self.context.profile['isAdmin']:
            sophomorixCommand = ['sophomorix-project', '--kill', '-p', projectName, '-jj']
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

        projectName = unquote(project.encode('latin-1'))
        ## Projectname must be in lowercase to avoid conflicts
        sophomorixCommand = ['sophomorix-project',  '--admins', username, '--create', '-p', projectName.lower(), '--school', schoolname, '-jj']
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

        attribute  = http_context.json_body()['attribute']
        value  = http_context.json_body()['value']
        groupType = http_context.json_body()['type']

        school = self.context.schoolmgr.school

        if attribute not in ["sophomorixJoinable", "sophomorixHidden", "sophomorixMailList"]:
            raise EndpointError(f"Modification of attribute {attribute} not supported")
        if value not in [True, False]:
            raise EndpointError(f"Value {value} is not a boolean")

        groupname = unquote(group.encode('latin-1'))

        if groupType == "project":
            if os.getuid() == 0:
                writer = LMNProject(groupname, school=school)
            else:
                # lmntools writers not supported for users actually
                if value:
                    prefix = "--"
                else:
                    prefix = "--no"

                if "Join" in attribute:
                    option = prefix + "join"
                elif "Hidden" in attribute:
                    option = prefix + "hide"
                elif "MailList" in attribute:
                    option = prefix + "maillist"

                sophomorixCommand = ['sophomorix-project', option, '--project', groupname, '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')

                if result['TYPE'] == "ERROR":
                    raise EndpointError(result['MESSAGE_EN'])
                else:
                    return f"Attribute {attribute} updated!"

        elif groupType == "class":
            writer = LMNSchoolclass(groupname, school=school)
        else:
            # group, i.e. printer
            writer = LMNPrinter(groupname, school=school)

        try:
            writer.setattr(data={attribute:value})
            return f"Attribute {attribute} updated!"
        except Exception as err:
            raise EndpointError(str(err))

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
            # Special case for project: user must be removed from admins and members
            'removeproject',
        ]

        if action in possible_actions:
            entities = [e for e in entity.split(',') if e]

            if objtype == 'group':
                # Printers go through linuxmuster-api: one LDAP modify for the
                # whole list, instead of one sophomorix-group call per entity.
                return self.set_printer_members(action, groupname, entities)

            # Projects and schoolclasses stay on sophomorix, which carries real
            # business logic there (home directories, quotas, exam mode).
            if action == 'removeproject':
                option = ["--removemembers", entity, "--removeadmins", entity]
            else:
                option = [f"--{action}", entity]

            sophomorixCommand = ['sophomorix-'+objtype,  *option, '--'+objtype, groupname, '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
            if result['TYPE'] == "ERROR":
                return result['TYPE'], result['MESSAGE_EN']
            return result['TYPE'], result['LOG']

    def set_printer_members(self, action, printer, entities):
        """
        Add or remove printer members through linuxmuster-api.

        Administrators patch the member list directly. A teacher may only
        join or quit a joinable printer themselves, which is what the printer
        checkbox does; the API enforces both rules on its side.

        :return: (TYPE, message), the tuple the frontend tests in equality
        :rtype: tuple
        """

        username = self.context.identity

        try:
            if self.context.profile['isAdmin']:
                self.context.lmnapi_client.patch_printer_members(printer, {action: entities})
            elif entities != [username]:
                return 'ERROR', 'Only administrators can change the members of a printer.'
            elif action == 'addmembers':
                self.context.lmnapi_client.join_printer(printer)
            elif action == 'removemembers':
                self.context.lmnapi_client.quit_printer(printer)
            else:
                return 'ERROR', 'Only administrators can change the members of a printer.'
        except (AttributeError, lmnapi_client.LmnapiUnavailable):
            return 'ERROR', LMNAPI_UNAVAILABLE_MESSAGE
        except lmnapi_client.LmnapiError as e:
            return 'ERROR', str(e)

        return 'LOG', f'Members of {printer} updated.'

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
                if details.get('sophomorixRole', '') == 'examuser':
                    # An exam account is a copy of a real one, killed when the
                    # exam is over: offering it here only ever adds a member
                    # that will silently vanish. Its label barely differs from
                    # the real account, so it is easy to pick by mistake.
                    continue

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


        if self.context.profile['isAdmin']:
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
