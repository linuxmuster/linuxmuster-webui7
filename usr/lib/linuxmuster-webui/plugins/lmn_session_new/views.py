from concurrent import futures
import logging
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
                'type': 'session'
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
            details = self.context.ldapreader.schoolget(f'/users/{user}')
            details['changed'] = False
            details['exammode-changed'] = False
            result.append(details)

        users = http_context.json_body()['users']
        with futures.ThreadPoolExecutor() as executor:
            infos = executor.map(get_user_info, users)
        return(result)

    @put(r'/api/lmn/session/sessions/(?P<session>[\w\+\-]*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_put_session(self, http_context, session=None):
        supervisor = self.context.identity
        sophomorixCommand = ['sophomorix-session', '--create', '--supervisor', supervisor, '-j', '--comment', session]

        if "members" in http_context.json_body():
            members = http_context.json_body()['members']
            membersList = [p['sAMAccountName'] for p in members]
            sophomorixCommand.extend(['--participants', ','.join(membersList)])

        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        return result

    @delete(r'/api/lmn/session/sessions/(?P<session>[\w\+\-]*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_delete_session(self, http_context, session=None):
        sophomorixCommand = ['sophomorix-session', '-j', '--session', session, '--kill']
        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        return result

    @patch(r'/api/lmn/session/exam/(?P<session>[\w\+\-]*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_end_exam(self, http_context, session=None):
        supervisor = http_context.json_body()['supervisor']
        participant = http_context.json_body()['participant']
        now = strftime("%Y%m%d_%H-%M-%S", localtime())
        try:
            sophomorixCommand = ['sophomorix-exam-mode', '--unset', '--subdir', 'transfer/collected/'+now+'-'+session+'-ended-by-'+supervisor+'/exam', '-j', '--participants', participant]
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

        try:
            sophomorixCommand = ['sophomorix-managementgroup', f'--{group}', usersList, '-jj']
            lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        except Exception as e:
            raise Exception(f'Error:\n{" ".join(sophomorixCommand)}\n Error was: {e}')

    @post(r'/api/lmn/session/participants')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_session_add_particpants(self, http_context):
        sessionID = http_context.json_body()['session']
        users = ','.join(http_context.json_body()['users'])
        sophomorixCommand = ['sophomorix-session', '-j', '--session', sessionID, '--add-participants', users]
        result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        return result

    @patch(r'/api/lmn/session/participants')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_session_remove_particpants(self, http_context):
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

        # if action == 'update-session':
        #     supervisor = http_context.json_body()['username']
        #     sessionID = http_context.json_body()['sessionID']
        #     if "participants" in http_context.json_body():
        #         participantsArray = http_context.json_body()['participants']
        #         participants = ','.join(participantsArray)
        #         sophomorixCommand = ['sophomorix-session', '--session', sessionID, '--supervisor', supervisor,  '-j', '--participants', participants]
        #     else:
        #         sophomorixCommand = ['sophomorix-session', '--session', sessionID, '--supervisor', supervisor,  '-j', '--participants', '']
        #     result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        #     return result
        #
        # if action == 'save-session':
        #     session = http_context.json_body()['session']
        #     sessionName = http_context.json_body()['sessionName']
        #     supervisor = http_context.json_body()['username']
        #     participants = http_context.json_body()['participants']
        #     participantsList = []
        #     now = strftime("%Y%m%d_%H-%M-%S", localtime())
        #
        #     examModeList, noExamModeList = [], []
        #
        #     for participant in participants:
        #         name = participant['sAMAccountName'].replace('-exam', '')
        #         participantsList.append(name)
        #
        #         # Only check for exammode if this value was changed in WEBUI
        #         if participant['exammode-changed'] is True:
        #             examModeList.append(name) if participant['exammode_boolean'] is True else noExamModeList.append(name)
        #
        #     # Save session members
        #     try:
        #         sophomorixCommand = ['sophomorix-session', '--session', session,  '-j', '--participants', ','.join(participantsList)]
        #         result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
        #     except Exception:
        #         raise Exception(f'Error:\nsophomorix-session --session {session} -j --participants {",".join(participantsList)}')
        #     # Put chosen members in exam mode
        #     try:
        #         if examModeList:
        #             sophomorixCommand = ['sophomorix-exam-mode', '--set', '--supervisor', supervisor, '-j', '--participants', ','.join(examModeList)]
        #             result = lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        #     except Exception:
        #         raise Exception(f'Error:\nsophomorix-exam-mode --set --supervisor {supervisor} -j --participants {",".join(examModeList)}')
        #     # Remove chosen members from exam mode
        #     try:
        #         if noExamModeList:
        #             sophomorixCommand = ['sophomorix-exam-mode', '--unset', '--subdir', f'transfer/collected/{now}-{sessionName}/exam', '-j', '--participants', ','.join(noExamModeList)]
        #             result = lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        #     except Exception:
        #         raise Exception(f'Error:\nsophomorix-exam-mode --unset --subdir {session} -j --participants {",".join(noExamModeList)}')
        #     return result
        # return 0

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
                "usersList": response.keys() if response else [],
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
        userList = self.context.ldapreader.schoolget(f'/users/search/student/{query}')
        return sorted(userList, key=lambda d: f"{d['sophomorixAdminClass']}{d['sn']}{d['givenName']}")

    @get(r'/api/lmn/session/schoolClass-search/(?P<query>.*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_ldap_group_search(self, http_context, query=''):
        return self.context.ldapreader.schoolget(f'/schoolclasses/search/{query}', sortkey='cn')

    @post(r'/api/lmn/session/moveFileToHome')  ## TODO authorize
    @endpoint(api=True)
    def handle_api_create_dir(self, http_context):
        """Create directory with given path, ignoring errors"""
        user = http_context.json_body()['user']
        filepath = http_context.json_body()['filepath']
        subdir = http_context.json_body()['subdir']
        try:
            sophomorixCommand = ['sophomorix-transfer', '--from-unix-path', filepath, '--to-user', user, '--subdir', subdir, '-jj']
            return lmn_getSophomorixValue(sophomorixCommand, '', True)
        except Exception:
            return 0

    @post(r'/api/lmn/session/trans-list-files')
    @endpoint(api=True)
    def handle_api_session_file_trans_list(self, http_context):
        user = http_context.json_body()['user']
        # check if user is a string(given by share option) or an object in an array (given by collect option)
        if not isinstance(user, str):
            user = user[0]['sAMAccountName']

        subfolderPath = ''
        if 'subfolderPath' in http_context.json_body():
            subfolderPath = http_context.json_body()['subfolderPath']
        sophomorixCommand = ['sophomorix-transfer', '-j', '--list-home-dir', user, '--subdir', f'/transfer/{subfolderPath}']
        availableFiles = lmn_getSophomorixValue(sophomorixCommand, 'sAMAccountName/'+user)
        availableFilesList = []
        if availableFiles['COUNT']['files'] == 0 and availableFiles['COUNT']['directories'] == 0:
            return availableFiles, []
        for availableFile in availableFiles['TREE']:
            availableFilesList.append(availableFile)
        return availableFiles, availableFilesList

    @post(r'/api/lmn/session/share')
    @authorize('lmn:session:trans')
    @endpoint(api=True)
    def handle_api_session_share(self, http_context):
        sender = self.context.identity
        receivers = http_context.json_body()['receivers']
        files = http_context.json_body()['files']
        session = http_context.json_body()['session']
        now = strftime("%Y%m%d_%H-%M-%S", localtime())

        def shareFiles(data):
            file, receiver = data
            sophomorixCommand = [
                'sophomorix-transfer',
                '-jj',
                '--scopy',
                '--from-user', sender,
                '--to-user', receiver,
                '--from-path', f'transfer/{file}',
                '--to-path', f'transfer/{now}_{sender}_{session}/'
            ]
            return lmn_getSophomorixValue(sophomorixCommand, '')

        try:
            to_share = [(f,r) for f in files for r in receivers]
            with futures.ThreadPoolExecutor() as executor:
                returnMessage = executor.map(shareFiles, to_share)
            print(returnMessage)
        except Exception as e:
            raise Exception('Something went wrong. Error:\n' + str(e))

    @post(r'/api/lmn/session/collect')
    @authorize('lmn:session:trans') # TODO
    @endpoint(api=True)
    def handle_api_session_collect(self, http_context):
        receiver = self.context.identity
        senders = http_context.json_body()['senders']
        files = http_context.json_body()['files']
        mode = http_context.json_body()['mode']
        session = http_context.json_body()['session']
        now = strftime("%Y%m%d_%H-%M-%S", localtime())

        if mode not in ['scopy', 'move']:
            return # TODO

        def collectFiles(data):
            file, sender = data
            sophomorixCommand = [
                'sophomorix-transfer',
                '-jj',
                f'--{mode}',
                '--from-user', sender,
                '--to-user', receiver,
                '--from-path', f'transfer/{receiver}_{session}/{file}',
                '--to-path', f'transfer/collected/{now}_{session}/'
            ]
            return lmn_getSophomorixValue(sophomorixCommand, '')

        try:
            to_collect = [(f,s) for f in files for s in senders]
            with futures.ThreadPoolExecutor() as executor:
                returnMessage = executor.map(collectFiles, to_collect)
            print(returnMessage)
        except Exception as e:
            raise Exception('Something went wrong. Error:\n' + str(e))


    @post(r'/api/lmn/session/trans')
    @endpoint(api=True)
    def handle_api_session_file_trans(self, http_context):
        senders = http_context.json_body()['senders']
        command = http_context.json_body()['command']
        receivers = http_context.json_body()['receivers']
        files = http_context.json_body()['files']
        session = http_context.json_body()['session']
        now = strftime("%Y%m%d_%H-%M-%S", localtime())

        def shareFiles(file):
            sophomorixCommand = [
                'sophomorix-transfer',
                '-jj',
                '--scopy',
                '--from-user', sender,
                '--to-user', receiversCSV,
                '--from-path', f'transfer/{file}',
                '--to-path', f'transfer/{sender}_{session}/'
            ]
            return lmn_getSophomorixValue(sophomorixCommand, '')

        def collectFiles(file):
            sophomorixCommand = [
                'sophomorix-transfer',
                '-jj',
                '--scopy',
                '--from-user', sendersCSV,
                '--to-user', receiver,
                '--from-path', f'transfer/{receiver}_{session}/{file}',
                '--to-path', f'transfer/collected/{now}-{session}/',
                '--to-path-addon', 'fullinfo'
            ]
            return lmn_getSophomorixValue(sophomorixCommand, '')

        def moveFiles(file):
            sophomorixCommand = [
                'sophomorix-transfer',
                '-jj',
                '--move',
                '--from-user', sendersCSV,
                '--to-user', receiver,
                '--from-path', f'transfer/{receiver}_{session}/{file}',
                '--to-path', f'transfer/collected/{now}-{session}/',
                '--to-path-addon', 'fullinfo'
            ]
            return lmn_getSophomorixValue(sophomorixCommand, '')

        with authorize('lmn:session:trans'):
            if command == 'share':
                try:
                    for sender in senders:
                        # check if bulkmode (array of usernames) or single user (object containing username)
                        # if first element is not a string
                        if not isinstance(receivers[0], str):
                            receivers[0] = receivers[0]['sAMAccountName']
                        receiversCSV = ",".join(receivers)
                        with futures.ThreadPoolExecutor() as executor:
                            returnMessage = executor.map(shareFiles, files)
                        returnMessage = list(returnMessage)[-1]
                except Exception as e:
                    raise Exception('Something went wrong. Error:\n' + str(e))
            if command == 'copy':
                try:
                    for receiver in receivers:
                        #raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(senders))
                        sendersCSV = ''
                        for sender in senders:
                            sendersCSV += sender['sAMAccountName']+','
                        # if files is All we're automatically in bulk mode
                        if files == "All":
                            sophomorixCommand = ['sophomorix-transfer', '-jj', '--scopy', '--from-user', sendersCSV, '--to-user', receiver, '--from-path', 'transfer/'+receiver+'_'+session, '--to-path', 'transfer/collected/'+now+'-'+session+'/', '--to-path-addon', 'fullinfo',  '--no-target-directory']
                            returnMessage = lmn_getSophomorixValue(sophomorixCommand, '')
                        else:
                            with futures.ThreadPoolExecutor() as executor:
                                returnMessage = executor.map(collectFiles, files)
                            returnMessage = list(returnMessage)[-1]
                except Exception as e:
                    raise Exception('Something went wrong. Error:\n' + str(e))
            if command == 'move':
                try:
                    for receiver in receivers:
                        sendersCSV = ''
                        for sender in senders:
                            sendersCSV += sender['sAMAccountName']+','
                        # if files is All we're automatically in bulk mode
                        if files == "All":
                            sophomorixCommand = ['sophomorix-transfer', '-jj', '--move', '--keep-source-directory', '--from-user', sendersCSV, '--to-user', receiver, '--from-path', 'transfer/'+receiver+'_'+session, '--to-path', 'transfer/collected/'+now+'-'+session+'/', '--to-path-addon', 'fullinfo',  '--no-target-directory']
                            returnMessage = lmn_getSophomorixValue(sophomorixCommand, '')
                        else:
                            with futures.ThreadPoolExecutor() as executor:
                                returnMessage = executor.map(moveFiles, files)
                            returnMessage = list(returnMessage)[-1]
                except Exception as e:
                    raise Exception('Something went wrong. Error:\n' + str(e))
        # TODO: Figure out why return message changed
        #if returnMessage['TYPE'] == "ERROR":
        ##    return returnMessage['TYPE']['LOG']
        #return returnMessage['TYPE'], returnMessage['LOG']
        #return returnMessage['TYPE']['LOG']
        return returnMessage
