from jadi import component
from aj.api.http import url, HttpPlugin
from time import gmtime, strftime  # needed for timestamp in collect transfer
import six  # used to determine if given variable is string
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
        action = http_context.json_body()['action']
        if action == 'get-sessions':
            supervisor = http_context.json_body()['username']
            with authorize('lm:users:students:read'):
                try:
                    sophomorixCommand = ['sophomorix-session', '-i', '-jj', '--supervisor', supervisor]
                    sessions = lmn_getSophomorixValue(sophomorixCommand, '')
                # Most likeley key error 'cause no sessions for this user exist
                except Exception as e:
                    raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(e))
                    return 0
            sessionsList = []
            if supervisor not in sessions['SUPERVISOR_LIST']:
                sessionJson = {}
                sessionJson['SESSIONCOUNT'] = 0
                sessionsList.append(sessionJson)
                return sessionsList

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
        if action == 'get-participants':
            participantList = []
            supervisor = http_context.json_body()['username']
            session = http_context.json_body()['session']

            with authorize('lm:users:students:read'):
                    try:
                        sophomorixCommand = ['sophomorix-session', '-i', '-jj']
                        participants = lmn_getSophomorixValue(sophomorixCommand, 'ID/'+session+'/PARTICIPANTS', True)
                        i = 0
                        for participant in participants:
                            participantList.append(participants[participant])
                            participantList[i]['sAMAccountName'] = participant
                            #if participant.endswith('-exam'):
                            #    participantList[i]['sAMAccountname-basename'] = participant.replace('-exam', '')
                            #else:
                            #    participantList[i]['sAMAccountname-basename'] = participant
                            participantList[i]['changed'] = 'FALSE'
                            participantList[i]['exammode-changed'] = 'FALSE'
                            for key in participantList[i]:
                                if participantList[i][key] == 'TRUE':
                                    participantList[i][key] = True
                                if participantList[i][key] == 'FALSE':
                                    participantList[i][key] = False
                            i = i + 1
                    except Exception:
                        participantList = 'empty'

            return participantList
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
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
                return result
        if action == 'new-session':
            supervisor = http_context.json_body()['username']
            comment = http_context.json_body()['comment']
            with authorize('lm:users:students:read'):
                sophomorixCommand = ['sophomorix-session', '--create', '--supervisor', supervisor,  '-j', '--comment', comment]
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
                return result
        # TODO: Removed remove block in future release
        #if action == 'change-exam-supervisor':
        #    supervisor = http_context.json_body()['supervisor']
        #    participant = http_context.json_body()['participant']
        #    comment = http_context.json_body()['comment']
        #    with authorize('lm:users:students:read'):
        #        try:
        #            sophomorixCommand = ['sophomorix-exam-mode', '--unset', '--subdir', session, '-j', '--participants', participant]
        #            result = lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        #        except Exception as e:
        #            raise Exception('Error:\n' + str(e))
        #        try:
        #            sophomorixCommand = ['sophomorix-exam-mode', '--set', '--supervisor', supervisor, '-j', '--participants', participant]
        #            result = lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        #        except Exception as e:
        #            raise Exception('Error:\n' + str(e))
        if action == 'end-exam':
            supervisor = http_context.json_body()['supervisor']
            participant = http_context.json_body()['participant']
            sessionName = http_context.json_body()['sessionName']
            now = strftime("%Y%m%d_%H-%M-%S", gmtime())
            #raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(http_context.json_body()))

            with authorize('lm:users:students:read'):
                try:
                    sophomorixCommand = ['sophomorix-exam-mode', '--unset', '--subdir', 'transfer/collected/'+now+'-'+sessionName+'-ended-by-'+supervisor+'/exam', '-j', '--participants', participant]
                    result = lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
                except Exception  as e:
                    raise Exception('Error:\n' + str(e))

        if action == 'save-session':
            def checkIfUserInManagementGroup(participant, participantBasename, managementgroup, managementList, noManagementList):
                try:
                    boolean = participant[managementgroup]
                    if (boolean is True) or (boolean == 'TRUE'):
                        managementList.append(participantBasename)
                    else:
                        noManagementList.append(participantBasename)
                except KeyError:
                    noManagementList.append(participantBasename)
                    pass
                return 0

            session = http_context.json_body()['session']
            sessionName = http_context.json_body()['sessionName']
            supervisor = http_context.json_body()['username']
            participants = http_context.json_body()['participants']
            participantsList = []
            now = strftime("%Y%m%d_%H-%M-%S", gmtime())

            examModeList, noExamModeList, wifiList, noWifiList, internetList, noInternetList, intranetList, noIntranetList, webfilterList, noWebfilterList, printingList, noPrintingList = [], [], [], [], [], [], [], [], [], [], [], []
            # Remove -exam in username to keep username as it is insead of saving -exam usernames in session
            for participant in participants:
                if participant['sAMAccountName'].endswith('-exam'):
                    participantBasename = participant['sAMAccountName'].replace('-exam', '')
                else:
                    participantBasename = str(participant['sAMAccountName'])
                    #participant['sAMAccountName']

                # Fill lists from WebUI Output -> Create csv of session members
                # This will executed on every save
                participantsList.append(participantBasename)
                # Only check for exammode if this value was changed in WEBUI
                if participant['exammode-changed'] is True:
                    checkIfUserInManagementGroup(participant, participantBasename, 'exammode_boolean', examModeList, noExamModeList)
                # Only check for managementgroups if this value was changed in WEBUI
                if participant['changed'] is True:
                    checkIfUserInManagementGroup(participant, participant['sAMAccountName'], 'group_wifiaccess', wifiList, noWifiList)
                    checkIfUserInManagementGroup(participant, participant['sAMAccountName'], 'group_internetaccess', internetList, noInternetList)
                    checkIfUserInManagementGroup(participant, participant['sAMAccountName'], 'group_intranetaccess', intranetList, noIntranetList)
                    checkIfUserInManagementGroup(participant, participant['sAMAccountName'], 'group_webfilter', webfilterList, noWebfilterList)
                    checkIfUserInManagementGroup(participant, participant['sAMAccountName'], 'group_printing', printingList, noPrintingList)
                #i = i + 1


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


            # Set managementgroups
            try:
                sophomorixCommand = ['sophomorix-managementgroup',
                                                '--wifi', wifiListCSV, '--nowifi', noWifiListCSV,
                                                '--internet', internetListCSV, '--nointernet', noInternetListCSV,
                                                '--intranet', intranetListCSV, '--nointranet',  noIntranetListCSV,
                                                '--webfilter', webfilterListCSV, '--nowebfilter',  noWebfilterListCSV,
                                                '--printing', printingListCSV, '--noprinting', noPrintingListCSV,
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
                    sophomorixCommand = ['sophomorix-exam-mode', '--unset', '--subdir', 'transfer/collected/'+now+'-'+sessionName+'/exam', '-j', '--participants', noExamModeListCSV]
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
                sophomorixCommand = ['sophomorix-query', '-jj', '--schoolbase', school, '--student', '--user-basic', '--anyname', '*'+http_context.query['q']+'*']
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

    @url(r'/api/lmn/session/trans-list-files')
    @endpoint(api=True)
    def handle_api_session_file_trans_list(self, http_context):
        user = http_context.json_body()['user']
        # check if user is a string(given by share option) or an object in an array (given by collect option)
        if not isinstance(user, six.string_types):
            user = user[0]['sAMAccountName']

        subfolderPath = ''
        if 'subfolderPath' in http_context.json_body():
            subfolderPath = http_context.json_body()['subfolderPath']
        sophomorixCommand = ['sophomorix-transfer', '-j', '--list-home-dir', user, '--subdir', '/transfer'+subfolderPath]
        availableFiles = lmn_getSophomorixValue(sophomorixCommand, 'sAMAccountName/'+user)
        #raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(availableFiles))
        availableFilesList = []
        if availableFiles['COUNT']['files'] == 0 and availableFiles['COUNT']['directories'] == 0:
            return availableFiles, ['null']
        for availableFile in availableFiles['TREE']:
            availableFilesList.append(availableFile)
        return availableFiles, availableFilesList

    @url(r'/api/lmn/session/trans')
    @endpoint(api=True)
    def handle_api_session_file_trans(self, http_context):
        senders = http_context.json_body()['senders']
        command = http_context.json_body()['command']
        receivers = http_context.json_body()['receivers']
        files = http_context.json_body()['files']
        session = http_context.json_body()['session']
        now = strftime("%Y%m%d_%H-%M-%S", gmtime())

        with authorize('lmn:session:trans'):
            if command == 'share':
                try:
                    for sender in senders:
                        for receiver in receivers:
                            # check if bulkmode (array of usernames) or single user (object containing username)
                            if not isinstance(receiver, six.string_types):
                                receiverSAMAccountName = receiver['sAMAccountName']
                            else:
                                receiverSAMAccountName = receiver
                            for File in files:
                                sophomorixCommand = ['sophomorix-transfer', '-jj', '--scopy', '--from-user', sender, '--to-user', receiverSAMAccountName, '--from-path', 'transfer/'+File, '--to-path', 'transfer/'+File]
                                returnMessage = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                except Exception as e:
                    raise Exception('Something went wrong. Error:\n' + str(e))
            if command == 'copy':
                try:
                    for sender in senders:
                        for receiver in receivers:
                            # if files is All we're automatically in bulk mode
                            if files == "All":
                                sophomorixCommand = ['sophomorix-transfer', '-jj', '--scopy', '--from-user', sender['sAMAccountName'], '--to-user', receiver, '--from-path', 'transfer', '--to-path', 'transfer/collected/'+now+'-'+session+'/'+sender['sophomorixAdminClass']+'/'+sender['sn'].replace(' ','_')+'_'+sender['givenName'].replace(' ','_')+'/', '--no-target-directory']
                                returnMessage = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                            else:
                                for File in files:
                                    sophomorixCommand = ['sophomorix-transfer', '-jj', '--scopy', '--from-user', sender['sAMAccountName'], '--to-user', receiver, '--from-path', 'transfer/'+File, '--to-path', 'transfer/collected/'+now+'-'+session+'/'+sender['sophomorixAdminClass']+'/'+sender['sn'].replace(' ','_')+'_'+sender['givenName'].replace(' ','_')+'/'+File]
                                    returnMessage = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                except Exception as e:
                    raise Exception('Something went wrong. Error:\n' + str(e))
            if command == 'move':
                try:
                    for sender in senders:
                        for receiver in receivers:
                            # if files is All we're automatically in bulk mode
                            if files == "All":
                                sophomorixCommand = ['sophomorix-transfer', '-jj', '--move', '--keep-source-directory', '--from-user', sender['sAMAccountName'], '--to-user', receiver, '--from-path', 'transfer', '--to-path', 'transfer/collected/'+now+'-'+session+'/'+sender['sophomorixAdminClass']+'/'+sender['sn'].replace(' ','_')+'_'+sender['givenName'].replace(' ','_')+'/', '--no-target-directory']
                                returnMessage = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                            else:
                                for File in files:
                                    sophomorixCommand = ['sophomorix-transfer', '-jj', '--move', '--from-user', sender['sAMAccountName'], '--to-user', receiver, '--from-path', 'transfer/'+File, '--to-path', 'transfer/collected/'+now+'-'+session+'/'+sender['sophomorixAdminClass']+'/'+sender['sn'].replace(' ','_')+'_'+sender['givenName'].replace(' ','_')+'/'+File]
                                    returnMessage = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                except Exception as e:
                    raise Exception('Something went wrong. Error:\n' + str(e))
        if returnMessage['TYPE'] == "ERROR":
            return returnMessage['TYPE']['LOG']
        return returnMessage['TYPE'], returnMessage['LOG']
        return returnMessage['TYPE']['LOG']
        #return returnMessage
