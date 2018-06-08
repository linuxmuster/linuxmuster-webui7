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
                    sophomorixCommand = ['sophomorix-session', '-i', '-jj']
                    sessions = lmn_getSophomorixValue(sophomorixCommand, 'SUPERVISOR/'+supervisor+'/sophomorixSessions', True)
                # Most likeley key error 'cause no sessions for this user exist
                except Exception:
                    return 0
            return sessions
        if action == 'get-participants':
            supervisor = http_context.json_body()['username']
            session = http_context.json_body()['session']
            with authorize('lm:users:students:read'):
                    try:
                        sophomorixCommand = ['sophomorix-session', '-i', '-jj']
                        participants = lmn_getSophomorixValue(sophomorixCommand, 'SUPERVISOR/'+supervisor+'/sophomorixSessions/'+session+'/PARTICIPANTS', True)
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
                # raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(session))
                sophomorixCommand = ['sophomorix-session', '-j', '--session', session, '--kill']
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
                return result
        if action == 'rename-session':
            session = http_context.json_body()['session']
            comment = http_context.json_body()['comment']
            with authorize('lm:users:students:read'):
                # raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(comment)+ str(session))
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
            participants = http_context.json_body()['participants']
            participantsList = []

            wifiList, noWifiList, internetList, noInternetList, intranetList, noIntranetList, webfilterList, noWebfilterList, printingList, noPrintingList = [], [], [], [], [], [], [], [], [], []
            for participant in participants:
                participantsList.append(participant)
                checkIfUserInManagementGroup(participant, 'group_wifiaccess', wifiList, noWifiList)
                checkIfUserInManagementGroup(participant, 'group_internetaccess', internetList, noInternetList)
                checkIfUserInManagementGroup(participant, 'group_intranetaccess', intranetList, noIntranetList)
                checkIfUserInManagementGroup(participant, 'group_webfilter', webfilterList, noWebfilterList)
                checkIfUserInManagementGroup(participant, 'group_printing', printingList, noPrintingList)

            participantsCSV = ",".join(participantsList)

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

            try:
                sophomorixCommand = ['sophomorix-managementgroup', \
                                                '--wifi', wifiListCSV, '--nowifi', noWifiListCSV,\
                                                '--internet', internetListCSV, '--nointernet', noInternetListCSV,\
                                                '--intranet', intranetListCSV, '--nointranet',  noIntranetListCSV,\
                                                '--webfilter', webfilterListCSV, '--nowebfilter',  noWebfilterListCSV,\
                                                '--printing', printingListCSV, '--noprinting', noPrintingListCSV, \
                                                '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
                #result = lmn_getSophomorixValue('sophomorix-managementgroup \
                #                                --wifi "' + wifiListCSV + '" --nowifi "' + noWifiListCSV +
                #                                '" --internet "' + internetListCSV + '" --nointernet "' + noInternetListCSV +
                #                                '" --intranet "' + intranetListCSV + '" --nointranet "' + noIntranetListCSV +
                #                                '" --webfilter "' + webfilterListCSV + '" --nowebfilter "' + noWebfilterListCSV +
                #                                '" --printing "' + printingListCSV + '" --noprinting "' + noPrintingListCSV +
                #                                '" -jj ', 'OUTPUT/0/LOG')
            except Exception as e:
                raise Exception('Error:\n' + str('sophomorix-managementgroup \
                                                 --wifi "' + wifiListCSV + '" --nowifi "' + noWifiListCSV +
                                                 '" --internet "' + internetListCSV + '" --nointernet "' + noInternetListCSV +
                                                 '" --intranet "' + intranetListCSV + '" --nointranet "' + noIntranetListCSV +
                                                 '" --webfilter "' + webfilterListCSV + '" --nowebfilter "' + noWebfilterListCSV +
                                                 '" --printing "' + printingListCSV + '" --noprinting "' + noPrintingListCSV +
                                                 '" -jj ') + "\n Error was: " + str(e))
            try:
                sophomorixCommand = ['sophomorix-session', '--session', session,  '-j', '--participants', participantsCSV]
                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0/LOG')
            except Exception:
                raise Exception('Error:\n' + str('sophomorix-session --session ' + session + ' -j --participants ' + participantsCSV))

            # raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(participants))
            return result

        if http_context.method == 'POST':
            with authorize('lm:users:students:write'):
                return 0

    @url(r'/api/lmn/session/user-search')
    @endpoint(api=True)
    def handle_api_ldap_user_search(self, http_context):
        with authorize('lm:users:students:read'):
            try:
                sophomorixCommand = ['sophomorix-query', '-jj', '--schoolbase', 'default-school', '--student', '--user-full', '--anyname', '*'+http_context.query['q']+'*']
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
        with authorize('lm:users:students:read'):
            try:
                sophomorixCommand = ['sophomorix-query', '-jj', '--schoolbase', 'default-school', '--sam', '*'+http_context.query['q']+'*']
                schoolClasses = lmn_getSophomorixValue(sophomorixCommand, 'GROUP', True)
            except Exception:
                return 0
        schoolClassList = []
        for schoolClass in schoolClasses:
            schoolClassList.append(schoolClasses[schoolClass])
        return schoolClasses
