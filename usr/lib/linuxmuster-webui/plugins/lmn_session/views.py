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
        supervisor = self.context.identity
        try:
            sophomorixCommand = ['sophomorix-session', '-i', '-jj', '--supervisor', supervisor]
            sessions = lmn_getSophomorixValue(sophomorixCommand, '')
        except Exception as e:
            raise EndpointError(e)

        sessionsList = []
        if sessions['SESSIONCOUNT'] == 0:
            return []

        for session in sessions['SUPERVISOR'][supervisor]['sophomorixSessions']:
            sessionJson = {}
            sessionJson['ID'] = session
            sessionJson['COMMENT'] = sessions['SUPERVISOR'][supervisor]['sophomorixSessions'][session]['COMMENT']
            if 'PARTICIPANT_COUNT' not in sessions['SUPERVISOR'][supervisor]['sophomorixSessions'][session]:
                sessionJson['PARTICIPANT_COUNT'] = 0
            else:
                sessionJson['PARTICIPANT_COUNT'] = sessions['SUPERVISOR'][supervisor]['sophomorixSessions'][session]['PARTICIPANT_COUNT']
            sessionsList.append(sessionJson)
        return sessionsList

    @get(r'/api/lmn/session/sessions/(?P<session>[\w\+\-]*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_get_session(self, http_context, session=None):

        def convert_bool(value):
            if value == 'TRUE':
                return True
            if value == 'FALSE':
                return False
            return value

        participantList = []
        try:
            sophomorixCommand = ['sophomorix-session', '-i', '-jj', '--session', session]
            participants = lmn_getSophomorixValue(sophomorixCommand, f'ID/{session}/PARTICIPANTS', True)
            for user,details in participants.items():
                details['sAMAccountName'] = user
                details['changed'] = False
                details['exammode-changed'] = False
                details['internet'] = details['group_internetaccess']
                details['intranet'] = details['group_intranetaccess']
                details['wifi'] = details['group_wifiaccess']
                details['webfilter'] = details['group_webfilter']
                details['printing'] = details['group_printing']

                del details['group_internetaccess']
                del details['group_intranetaccess']
                del details['group_wifiaccess']
                del details['group_webfilter']
                del details['group_printing']

                for key,value in details.items():
                    details[key] = convert_bool(value)

                participantList.append(details)
        except KeyError as e:
            logging.info(f"No participants found in {e}")
        return participantList

    @get(r'/api/lmn/session/group/(?P<group>[\w\+\-]*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_get_group(self, http_context, group=None):
        participantList = []
        try:
            sophomorixCommand = ['sophomorix-query', '--group-members', '--user-full', '--sam', group, '-jj']
            participants = lmn_getSophomorixValue(sophomorixCommand, f'MEMBERS/{group}', True)
            for user,details in participants.items():
                details['sAMAccountName'] = user
                details['changed'] = False
                details['exammode-changed'] = False
                # TODO : default values ?
                details['internet'] = True
                details['intranet'] = True
                details['wifi'] = True
                details['webfilter'] = True
                details['printing'] = True

                if details['sophomorixRole'] == 'student':
                    participantList.append(details)
        except KeyError as e:
            logging.info(f"No participants found in {e}")
        return participantList

    @put(r'/api/lmn/session/sessions/(?P<session>[\w\+\-]*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_put_session(self, http_context, session=None):
        supervisor = self.context.identity
        sophomorixCommand = ['sophomorix-session', '--create', '--supervisor', supervisor, '-j', '--comment', session]

        if "participants" in http_context.json_body():
            participants = http_context.json_body()['participants']
            participantsList = [p['sAMAccountName'] for p in participants]
            sophomorixCommand.extend(['--participants', ','.join(participantsList)])

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
                "usersList": list(response.keys()),
                "room": room,
                "objects": response,
            }
        except IndexError as e :
            return 0

    @get(r'/api/lmn/session/user-search/(?P<query>.*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_ldap_user_search(self, http_context, query=''):
        schoolname = self.context.schoolmgr.school
        try:
            sophomorixCommand = ['sophomorix-query', '-jj', '--schoolbase', schoolname, '--student', '--user-basic', '--anyname', f'*{query}*']
            users = lmn_getSophomorixValue(sophomorixCommand, 'USER', True)
        except Exception:
            return 0
        userList = []
        for user in users:
            userList.append(users[user])
        return userList

    @get(r'/api/lmn/session/schoolClass-search/(?P<query>.*)')
    @authorize('lm:users:students:read')
    @endpoint(api=True)
    def handle_api_ldap_group_search(self, http_context, query=''):
        schoolname = self.context.schoolmgr.school
        try:
            sophomorixCommand = ['sophomorix-query', '-jj', '--schoolbase', schoolname, '--class', '--group-members', '--user-full', '--sam', f'*{query}*']
            schoolClasses = lmn_getSophomorixValue(sophomorixCommand, 'MEMBERS', True)
        except Exception:
            return 0
        schoolClassList = []
        for schoolClass in schoolClasses:
            schoolClassJson = {}
            schoolClassJson['sophomorixAdminClass'] = schoolClass
            schoolClassJson['members'] = schoolClasses[schoolClass]
            schoolClassList.append(schoolClassJson)
        return schoolClassList

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
