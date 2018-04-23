angular.module('lmn.session').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/session',
        controller: 'LMNSessionController'
        templateUrl: '/lmn_session:resources/partial/session.html'

#angular.module('lmn.session').controller 'LMNSESSIONModalController', ($scope, $uibModalInstance, $http, gettext, notify, messagebox, username, session, comment) ->
#    $scope.username = username
#    $scope.session = session
#    $scope.comment = comment
#
#    $scope.save = () ->
#       $uibModalInstance.close(session)
#
#    $scope.close = () ->
#       $uibModalInstance.dismiss()



angular.module('lmn.session').controller 'LMNSessionController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Session'))


    $scope.currentSession = {
        name: ""
        comment: ""
    }

    $scope.sorts = [
       {
          name: gettext('Login name')
          fx: (x) -> x.sAMAccountName
       }
       {
          name: gettext('Lastname')
          fx: (x) -> x.sn
       }
       {
          name: gettext('Firstname')
          fx: (x) -> x.givenName
       }
       {
          name: gettext('Email')
          fx: (x) -> x.mail
       }
    ]

    $scope.fields = {
       sAMAccountName:
          visible: true
          name: gettext('Loginname')
       name:
          visible: true
          name: gettext('Name')
       #sn:
       #  visible: true
       #  name: gettext('Lastname')
       #givenName:
       #   visible: true
       #   name: gettext('Firstname')
       examMode:
          visible: true
          name: gettext('Exam-Mode')
       wifiaccess:
          visible: true
          name: gettext('WifiAccess')
       internetaccess:
          visible: true
          name: gettext('Internet')
       intranetaccess:
          visible: true
          name: gettext('Intranet')
       webfilter:
          visible: true
          name: gettext('Webfilter')
       printing:
          visible: true
          name: gettext('Printing')
    }

    $scope.checkboxModel = {
       value1 : false,
       value2 : true
    }

    $scope.visible = {
       table : 'none',
       sessionname : 'none',
    }


    $scope.info = {
        message : ''
    }

    $scope._ =
            addParticipant: null


    $scope.killSession = (username,session) ->
                messagebox.show(text: "Delete '#{session}'?", positive: 'Delete', negative: 'Cancel').then () ->
                    $http.post('/api/lmn/session/sessions', {action: 'kill-sessions', session: session}).then (resp) ->
                        notify.success gettext('Session Deleted')

    $scope.newSession = (username) ->
                messagebox.prompt(gettext('Session Name'), '---').then (msg) ->
                    if not msg.value
                        return
                    $http.post('/api/lmn/session/sessions', {action: 'new-session', username: username, comment: msg.value}).then (resp) ->
                        $scope.new-sessions = resp.data
                        notify.success gettext('Session Created')

    $scope.showSessions = (username) ->
                $http.post('/api/lmn/session/sessions', {action: 'get-sessions', username: username}).then (resp) ->
                    $scope.sessions = resp.data
                    messagebox.show(title: gettext('Current Sessions'), text: $scope.sessions, positive: 'OK')

    $scope.getSessions = (username) ->
                $http.post('/api/lmn/session/sessions', {action: 'get-sessions', username: username}).then (resp) ->
                    #if resp.data is 0
                        #messagebox.show(title: gettext('No Sessions'), text: 'No session found! Please create a session first.', positive: 'OK')
                    $scope.sessions = resp.data


    $scope.renameSession = (username, session, comment) ->
        #messagebox.show(title: gettext('Current Sessions'), text: $scope.sessions, positive: 'OK')
                messagebox.prompt(gettext('Session Name'), comment).then (msg) ->
                    if not msg.value
                        return
                    $http.post('/api/lmn/session/sessions', {action: 'rename-session', session: session, comment: msg.value}).then (resp) ->
                        notify.success gettext('Session Renamed')

    $scope.getParticipants = (username,session) ->
                $http.post('/api/lmn/session/sessions', {action: 'get-participants', username: username, session: session}).then (resp) ->
                    $scope.visible.sessionname = 'show'
                    if resp.data is 0
                        $scope.visible.table = 'none'
                        $scope.info.message = 'This session appears to be empty. Start adding users by using the top search bar!'
                    else
                        $scope.info.message = ''
                        $scope.visible.table = 'show'
                    console.log resp.data
                    $scope.participants = resp.data

    $scope.findUsers = (q) ->
                return $http.get("/api/lmn/session/user-search?q=#{q}").then (resp) ->
                            $scope.users = resp.data
                            # console.log resp.data
                            return resp.data

    $scope.$watch '_.addParticipant', () ->
                if $scope._.addParticipant
                    $scope.info.message = ''
                    $scope.visible.table = 'show'
                    $scope.participants[$scope._.addParticipant.sAMAccountName] = angular.copy({"givenName":$scope._.addParticipant.givenName,"sn":$scope._.addParticipant.sn,
                    "sophomorixExamMode":$scope._.addParticipant.sophomorixExamMode,
                    "group_webfilter":$scope._.addParticipant.MANAGEMENTGROUPS.webfilter,
                    "group_intranetaccess":$scope._.addParticipant.MANAGEMENTGROUPS.intranet,
                    "group_printing":$scope._.addParticipant.MANAGEMENTGROUPS.printing,
                    "sophomorixStatus":"U","sophomorixRole":$scope._.addParticipant.sophomorixRole,
                    "group_internetaccess":$scope._.addParticipant.MANAGEMENTGROUPS.internet,
                    "sophomorixAdminClass":$scope._.addParticipant.sophomorixAdminClass,
                    "user_existing":true,"group_wifiaccess":$scope._.addParticipant.MANAGEMENTGROUPS.wifi})
                    $scope._.addParticipant = null

    $scope.removeParticipant = (participant) ->
                console.log $scope.participants
                console.log participant
                delete $scope.participants[participant]

    $http.get("/api/lmn/session").then (resp) ->
    #$http.get("/api/lmn/session/sessions").then (username,session) ->
                #$http.post('/api/lmn/session/sessions', {action: 'get-participants', username: username, session: session}).then (resp) ->
                    #$scope.sessions = resp.data
                #$scope.sessions = resp.data

    $scope.saveApply = (participants, session) ->
                $http.post('/api/lmn/session/sessions', {action: 'save-session', participants: participants, session: session}).then (resp) ->


    $scope.cancel = (username,session) ->
        $scope.getParticipants(username,session)

