from concurrent import futures
import logging
import subprocess
from time import localtime, strftime  # needed for timestamp in collect transfer

from jadi import component
from aj.api.http import get, post, put, patch, delete, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/session/sessions')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_get_sessions(self, http_context):
        user = self.context.identity

        sessions = self.context.ldapreader.schoolget(f'/users/{user}', dict=False).lmnsessions
        sessionsList = []
        for session in sessions:
            s = {
                'sid': session.sid,
                'name': session.name,
                'membersCount': session.membersCount,
                'members': session.members,
                'type': 'group'
            }
            sessionsList.append(s)
        return sessionsList

    @get(r'/api/lmn/session/schoolclasses')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_get_schoolclasses(self, http_context):
        user = self.context.identity

        schoolclasses = self.context.ldapreader.schoolget(f'/users/{user}', dict=False).schoolclasses
        schoolclassesList = []
        for schoolclass in schoolclasses:
            details = self.context.ldapreader.schoolget(f'/schoolclasses/{schoolclass}', dict=False)
            s = {
                'name': details.cn,
                'membersCount': len(details.sophomorixMembers),
                'members': details.sophomorixMembers,
                'type': 'schoolclass'
            }
            schoolclassesList.append(s)
        return schoolclassesList

    @get(r'/api/lmn/session/projects')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_get_projects(self, http_context):
        user = self.context.identity

        projects = self.context.ldapreader.schoolget(f'/users/{user}', dict=False).projects
        projectsList = []
        for project in projects:
            details = self.context.ldapreader.schoolget(f'/projects/{project}', dict=False)
            s = {
                'name': details.cn,
                'membersCount': len(details.sophomorixMembers),
                'members': details.sophomorixMembers,
                'type': 'project'
            }
            projectsList.append(s)
        return projectsList

    # TODO : post is wrong here
    @post(r'/api/lmn/session/userinfo')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_userinfo(self, http_context):

        result = []

        def get_user_info(user):
            baseUser = user.replace('-exam', '')
            details = self.context.ldapreader.schoolget(f'/users/{baseUser}')
            if self.context.identity in details['sophomorixExamMode']:
                details = self.context.ldapreader.schoolget(f'/users/exam/{user}')
            result.append(details)

        users = http_context.json_body()['users']
        with futures.ThreadPoolExecutor() as executor:
            infos = executor.map(get_user_info, users)
        return(result)

    # TODO : post is wrong here
    @post(r'/api/lmn/session/exam/userinfo')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_exam_userinfo(self, http_context):

        result = []

        def get_exam_user_info(user):
            details = self.context.ldapreader.schoolget(f'/users/exam/{user}')
            result.append(details)

        users = http_context.json_body()['users']
        with futures.ThreadPoolExecutor() as executor:
            infos = executor.map(get_exam_user_info, users)
        return(result)

    @put(r'/api/lmn/session/sessions/(?P<session>[\w\+\-]*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_put_session(self, http_context, session=None):
        supervisor = self.context.identity
        sophomorixCommand = ['sophomorix-session', '--create', '--supervisor', supervisor, '-j', '--comment', session]

        if "members" in http_context.json_body():
            members = http_context.json_body()['members']
            sophomorixCommand.extend(['--participants', ','.join(members)])

        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        return result

    @delete(r'/api/lmn/session/sessions/(?P<session>[\w\+\-]*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_delete_session(self, http_context, session=None):
        sophomorixCommand = ['sophomorix-session', '-j', '--session', session, '--kill']
        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        return result

    @patch(r'/api/lmn/session/exam/start')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_start_exam(self, http_context):
        supervisor = self.context.identity
        session = http_context.json_body()['session']
        participants = ','.join([member['cn'] for member in session['members']])

        try:
            sophomorixCommand = [
                'sophomorix-exam-mode',
                '--set',
                '--supervisor', supervisor,
                '-j',
                '--participants', participants
            ]
            lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        except Exception as e:
            raise Exception('Error:\n' + str(e))

    @patch(r'/api/lmn/session/exam/stop')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_stop_exam(self, http_context):
        session = http_context.json_body()['session']
        participants = ','.join([member['cn'] for member in session['members']])
        group_type = _(session['type'])
        group_name = session['name']

        now = strftime("%Y-%m-%d_%Hh%Mm%S", localtime())
        target = f'EXAM_{group_type}_{group_name}_{now}'

        try:
            sophomorixCommand = [
                'sophomorix-exam-mode',
                '--unset',
                '--subdir', f'transfer/collected/{target}',
                '-j',
                '--participants', participants
            ]
            lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        except Exception as e:
            raise Exception('Error:\n' + str(e))

    @post(r'/api/lmn/managementgroup')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_management_group(self, http_context):
        users = http_context.json_body()['users']
        usersList = ','.join(users) if len(users) > 1 else users[0]
        group = http_context.json_body()['group']

        groups = ['wifi', 'internet', 'intranet', 'webfilter', 'printing']
        valid_groups = groups + [f'no{g}' for g in groups]

        if group not in valid_groups:
            return

        action = "--add-members"
        if group.startswith("no"):
            action = "--remove-members"
            group = group[2:]

        p = subprocess.Popen([
            'sudo',
            '/usr/local/sbin/lmntools-managementgroup',
            '-g', group,
            '-s', self.context.schoolmgr.school,
            action, usersList],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
        )
        stdout, stderr = p.communicate()

        if stderr:
            raise Exception(stderr.decode())

    @post(r'/api/lmn/session/participants')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_session_add_participants(self, http_context):
        sessionID = http_context.json_body()['session']
        users = ','.join(http_context.json_body()['users'])
        sophomorixCommand = ['sophomorix-session', '-j', '--session', sessionID, '--add-participants', users]
        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        return result

    @patch(r'/api/lmn/session/participants')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_session_remove_participants(self, http_context):
        sessionID = http_context.json_body()['session']
        users = ','.join(http_context.json_body()['users'])
        sophomorixCommand = ['sophomorix-session', '-j', '--session', sessionID, '--remove-participants', users]
        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        return result

    @post(r'/api/lmn/session/sessions')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_session_sessions(self, http_context):
        sessionID = http_context.json_body()['session']
        comment = http_context.json_body()['comment']
        sophomorixCommand = ['sophomorix-session', '-j', '--session', sessionID, '--comment', comment]
        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        return result

    @get(r'/api/lmn/session/userInRoom')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_get_user_in_room(self, http_context):
        schoolname = self.context.schoolmgr.school
        username = self.context.identity
        try:
            sophomorixCommand = ['sophomorix-query', '-jj', '--smbstatus', '--schoolbase', schoolname, '--query-user', username]
            response = lmn_getSophomorixValue(sophomorixCommand, '')
            # remove our own
            room = response[username]['ROOM']
            response.pop(username, None)
            return {
                "usersList": list(response.keys()) if response else [],
                "name": room,
                "objects": response,
            }
        except IndexError as e:
            # response is an empty dict, not able to detect the room
            # or the other users in room
            return {
                "usersList": [],
                "name": '',
                "objects": {},
            }

    @get(r'/api/lmn/session/user-search/(?P<query>.*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_ldap_user_search(self, http_context, query=''):
        query = query.encode("latin-1").decode("utf-8")
        for char in query:
            # Ignoring non alnum queries like "ger¨"
            if not char.isalnum():
                return
        userList = self.context.ldapreader.schoolget(f'/users/search/student/{query}')
        return sorted(userList, key=lambda d: f"{d['sophomorixAdminClass']}{d['sn']}{d['givenName']}")

    @get(r'/api/lmn/session/schoolClass-search/(?P<query>.*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_ldap_group_search(self, http_context, query=''):
        query = query.encode("latin-1").decode("utf-8")
        for char in query:
            # Ignoring non alnum queries like "ger¨"
            if not char.isalnum():
                return
        return self.context.ldapreader.schoolget(f'/schoolclasses/search/{query}', sortkey='cn')

    @post(r'/api/lmn/session/moveFileToHome')  ## TODO authorize
    @endpoint(api=True)
    def handle_api_create_dir(self, http_context):
        """
        Create directory with given path, ignoring errors
        Only used in upload service. Deprecated ?
        """

        user = http_context.json_body()['user']
        filepath = http_context.json_body()['filepath']
        subdir = http_context.json_body()['subdir']
        try:
            sophomorixCommand = ['sophomorix-transfer', '--from-unix-path', filepath, '--to-user', user, '--subdir', subdir, '-jj']
            return lmn_getSophomorixValue(sophomorixCommand, '', True)
        except Exception:
            return 0

