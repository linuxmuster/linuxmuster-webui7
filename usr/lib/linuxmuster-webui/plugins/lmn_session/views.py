from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import authorize
from aj.plugins.lm_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/session/sessions')
    @endpoint(api=True)
    def handle_api_session_sessions(self, http_context):
        # sessionsList = []
        action = http_context.json_body()['action']
        if action == 'get-sessions':
            supervisor = http_context.json_body()['username']
            with authorize('lm:users:students:read'):
                try:
                    sophomorixCommand = ['sophomorix-session', '-i', '-jj', '--supervisor', supervisor]
                    sessions = lmn_getSophomorixValue(sophomorixCommand, 'SUPERVISOR/'+supervisor+'/sophomorixSessions', True)
                # Most likeley key error 'cause no sessions for this user exist
                except Exception as e:
                    raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(e))
                    return 0
            sessionsList = []
            for session in sessions:
                sessionJson = {}
                sessionJson['ID'] = session
                sessionJson['COMMENT'] = sessions[session]['COMMENT']
                if 'PARTICIPANT_COUNT' not in sessions[session]:
                    sessionJson['PARTICIPANT_COUNT'] = 0
                else:
                    sessionJson['PARTICIPANT_COUNT'] = sessions[session]['PARTICIPANT_COUNT']
                sessionsList.append(sessionJson)
            return sessionsList
        if action == 'get-participants':
            supervisor = http_context.json_body()['username']
            session = http_context.json_body()['session']
            with authorize('lm:users:students:read'):
                    try:
                        sophomorixCommand = ['sophomorix-session', '-i', '-jj']
                        participants = lmn_getSophomorixValue(sophomorixCommand, 'ID/'+session+'/PARTICIPANTS', True)
                    except Exception:
                        participants = {'0': {"givenName": "null", "sophomorixExamMode": "---", "group_wifiaccess": False, "group_intranetaccess": False, "group_printing": False, "sophomorixStatus": "U", "sophomorixRole": "", "group_internetaccess": False, "sophomorixAdminClass": "", "group_webfilter": False, "user_existing": False, "sn": ""}}
                        #return ["frayka"["test":"null"]]
                    # Convert PERL bool to python bool
                    for key, value in participants.iteritems():
                        for key in value:
                            if value[key] == 'TRUE':
                                value[key] = True
                            if value[key] == 'FALSE':
                                value[key] = False
            return participants
        if action == 'kill-sessions':
            session = http_context.json_body()['session']
            with authorize('lm:users:students:read'):
                sophomorixCommand = ['sophomorix-session', '-j', '--session', session, '--kill']
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
                return result
        if action == 'rename-session':
            session = http_context.json_body()['session']
            comment = http_context.json_body()['comment']
            with authorize('lm:users:students:read'):
                sophomorixCommand = ['sophomorix-session', '-j', '--session', session, '--comment', comment]
                result = lmn_getSophomorixValue(sophomorixCommand , 'OUTPUT/0/LOG')
                return result
        if action == 'new-session':
            supervisor = http_context.json_body()['username']
            comment = http_context.json_body()['comment']
            with authorize('lm:users:students:read'):
                sophomorixCommand = ['sophomorix-session', '--create', '--supervisor', supervisor,  '-j', '--comment', comment]
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
                return result
        if action == 'change-exam-supervisor':
            supervisor = http_context.json_body()['supervisor']
            participant= http_context.json_body()['participant']
            comment = http_context.json_body()['comment']
            with authorize('lm:users:students:read'):
                try:
                    sophomorixCommand = ['sophomorix-exam-mode', '--unset', '--subdir', session, '-j', '--participants', participant]
                    result = lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
                except Exception:
                    raise Exception('Error:\n' + str('sophomorix-exam-mode --set --supervisor ' + supervisor + ' -j --participants ' + participant))
                try:
                    sophomorixCommand = ['sophomorix-exam-mode', '--set', '--supervisor', supervisor, '-j', '--participants', participant]
                    result = lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
                except Exception:
                    raise Exception('Error:\n' + str('sophomorix-exam-mode --unset --subdir ' + session + ' -j --participants ' + participant))
        if action == 'save-session':
            def checkIfUserInManagementGroup(participant, managementgroup, managementList, noManagementList):
                try:
                    boolean = participants[participant][managementgroup]
                    if (boolean is True) or (boolean == 'TRUE'):
                        managementList.append(participant)
                    else:
                        noManagementList.append(participant)
                except KeyError:
                    noManagementList.append(participant)
                    pass
                return 0

            session = http_context.json_body()['session']
            supervisor = http_context.json_body()['username']
            participants = http_context.json_body()['participants']
            participantsList = []

            examModeList, noExamModeList, wifiList, noWifiList, internetList, noInternetList, intranetList, noIntranetList, webfilterList, noWebfilterList, printingList, noPrintingList = [], [], [], [], [], [], [], [], [], [], [], []
            # Remove -exam in username to keep username as it is insead of saving -exam usernames in session
            for participant in participants:
                if participant.endswith('-exam'):
                    participant = participant.replace('-exam','')
                # Fill lists from WebUI Output
                participantsList.append(participant)
                checkIfUserInManagementGroup(participant, 'exammode_boolean', examModeList, noExamModeList)
                checkIfUserInManagementGroup(participant, 'group_wifiaccess', wifiList, noWifiList)
                checkIfUserInManagementGroup(participant, 'group_internetaccess', internetList, noInternetList)
                checkIfUserInManagementGroup(participant, 'group_intranetaccess', intranetList, noIntranetList)
                checkIfUserInManagementGroup(participant, 'group_webfilter', webfilterList, noWebfilterList)
                checkIfUserInManagementGroup(participant, 'group_printing', printingList, noPrintingList)



            # Create CSV lists we need for sophomorix
            participantsCSV = ",".join(participantsList)
            examModeListCSV = ",".join(examModeList)
            noExamModeListCSV = ",".join(noExamModeList)
            wifiListCSV = ",".join(wifiList)
            noWifiListCSV = ",".join(noWifiList)
            internetListCSV = ",".join(internetList)
            noInternetListCSV = ",".join(noInternetList)
            intranetListCSV = ",".join(intranetList)
            noIntranetListCSV = ",".join(noIntranetList)
            webfilterListCSV = ",".join(webfilterList)
            noWebfilterListCSV = ",".join(noWebfilterList)
            printingListCSV = ",".join(printingList)
            noPrintingListCSV = ",".join(noPrintingList)

            #raise Exception('Error:\n' + str(noExamModeListCSV))

            # Set managementgroups
            try:
                sophomorixCommand = ['sophomorix-managementgroup', \
                                                '--wifi', wifiListCSV, '--nowifi', noWifiListCSV,\
                                                '--internet', internetListCSV, '--nointernet', noInternetListCSV,\
                                                '--intranet', intranetListCSV, '--nointranet',  noIntranetListCSV,\
                                                '--webfilter', webfilterListCSV, '--nowebfilter',  noWebfilterListCSV,\
                                                '--printing', printingListCSV, '--noprinting', noPrintingListCSV, \
                                                '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
            except Exception as e:
                raise Exception('Error:\n' + str('sophomorix-managementgroup \
                                                 --wifi "' + wifiListCSV + '" --nowifi "' + noWifiListCSV +
                                                 '" --internet "' + internetListCSV + '" --nointernet "' + noInternetListCSV +
                                                 '" --intranet "' + intranetListCSV + '" --nointranet "' + noIntranetListCSV +
                                                 '" --webfilter "' + webfilterListCSV + '" --nowebfilter "' + noWebfilterListCSV +
                                                 '" --printing "' + printingListCSV + '" --noprinting "' + noPrintingListCSV +
                                                 '" -jj ') + "\n Error was: " + str(e))
            # Save session members
            try:
                sophomorixCommand = ['sophomorix-session', '--session', session,  '-j', '--participants', participantsCSV]
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
            except Exception:
                raise Exception('Error:\n' + str('sophomorix-session --session ' + session + ' -j --participants ' + participantsCSV))
            # Put chosen members in exam mode
            try:
                if examModeListCSV != "":
                    sophomorixCommand = ['sophomorix-exam-mode', '--set', '--supervisor', supervisor, '-j', '--participants', examModeListCSV]
                    result = lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
            except Exception:
                raise Exception('Error:\n' + str('sophomorix-exam-mode --set --supervisor ' + supervisor + ' -j --participants ' + examModeListCSV))
            # Remove chosen members from exam mode
            try:
                if noExamModeListCSV != "":
                    sophomorixCommand = ['sophomorix-exam-mode', '--unset', '--subdir', session, '-j', '--participants', noExamModeListCSV]
                    result = lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
            except Exception:
                raise Exception('Error:\n' + str('sophomorix-exam-mode --unset --subdir ' + session + ' -j --participants ' + noExamModeListCSV))

            return result

        if http_context.method == 'POST':
            with authorize('lm:users:students:write'):
                return 0

    @url(r'/api/lmn/session/user-search')
    @endpoint(api=True)
    def handle_api_ldap_user_search(self, http_context):
        school = 'default-school'
        with authorize('lm:users:students:read'):
            try:
                sophomorixCommand = ['sophomorix-query', '-jj', '--schoolbase', school, '--student', '--user-full', '--anyname', '*'+http_context.query['q']+'*']
                users = lmn_getSophomorixValue(sophomorixCommand, 'USER', True)
            except Exception:
                return 0
        userList = []
        for user in users:
            userList.append(users[user])
        return userList

    @url(r'/api/lmn/session/schoolClass-search')
    @endpoint(api=True)
    def handle_api_ldap_group_search(self, http_context):
        school = 'default-school'
        with authorize('lm:users:students:read'):
            try:
                sophomorixCommand = ['sophomorix-query', '-jj', '--schoolbase', school, '--class', '--group-members', '--user-full', '--sam', '*'+http_context.query['q']+'*']
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

    @url(r'/api/lmn/session/trans')
    @endpoint(api=True)
    def handle_api_session_file_trans(self, http_context):
        senders = http_context.json_body()['senders']
        #sender  = ','.join([x.strip() for x in senders])
        #transTitle = http_context.json_body()['transTitle']
        command = http_context.json_body()['command']
        receivers = http_context.json_body()['receivers']
        receiver  = ','.join([x.strip() for x in receivers])
        with authorize('lmn:session:trans'):
            if command == 'copy':
                try:
                    for sender in senders:
                        sophomorixCommand = ['sophomorix-transfer', '-jj', '--collect-copy', '--from-user', sender, '--to-user', receiver, '--file', 'transfer']
                        returnMessage = lmn_getSophomorixValue(sophomorixCommand, 'JSONINFO')
                except Exception as e:
                    raise Exception('Something went wrong. Error:\n' + str(e))
            if command == 'move':
                try:
                    for sender in senders:
                        sophomorixCommand = ['sophomorix-transfer', '-jj', '--collect-move', '--from-user', sender, '--to-user', receiver, '--file', 'transfer/']
                        returnMessage = lmn_getSophomorixValue(sophomorixCommand, 'JSONINFO')
                except Exception as e:
                    raise Exception('Something went wrong. Error:\n' + str(e))
        return returnMessage
