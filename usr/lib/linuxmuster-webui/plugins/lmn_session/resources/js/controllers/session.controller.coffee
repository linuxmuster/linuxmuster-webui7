angular.module('lmn.session').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/session',
        controller: 'LMNSessionController'
        templateUrl: '/lmn_session:resources/partial/session.html'

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
       sn:
          visible: true
          name: gettext('Lastname')
       givenName:
          visible: true
          name: gettext('Firstname')
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
       value2 : 'true'
    }

    $scope.killSession = (username,session) ->
                #if confirm "Delete Session ?"
                $http.post('/api/lmn/session/sessions', {action: 'kill-sessions', session: session}).then (resp) ->
                    messagebox.show(title: gettext('Sessions Removed'), text: 'Session '+session +'removed', positive: 'OK')

    $scope.newSession = (username) ->
                $http.post('/api/lmn/session/sessions', {action: 'new-session', username: username}).then (resp) ->
                    $scope.new-sessions = resp.data

    $scope.showSessions = (username) ->
                $http.post('/api/lmn/session/sessions', {action: 'get-sessions', username: username}).then (resp) ->
                    $scope.sessions = resp.data
                    messagebox.show(title: gettext('Current Sessions'), text: $scope.sessions, positive: 'OK')

    $scope.getSessions = (username) ->
                $http.post('/api/lmn/session/sessions', {action: 'get-sessions', username: username}).then (resp) ->
                    $scope.sessions = resp.data

    $scope.renameSession = (username, session) ->
                $uibModal.open(
                   templateUrl: '/lm_linbo:resources/partial/image.modal.html'
                   controller: 'LMLINBOImageModalController'
                   #resolve:
                   #   image: () -> angular.copy(image)
                   #   images: () -> $scope.images
                ).result.then (result) ->
                   $http.post('/api/lmn/session/sessions', {action: 'rename-sessions', username: username, session: session, comment: comment}).then (resp) ->
                      notify.success gettext('Saved')



    $scope.getParticipants = (username,session) ->
                $http.post('/api/lmn/session/sessions', {action: 'get-participants', username: username, session: session}).then (resp) ->
                    $scope.participants = resp.data


    $http.get("/api/lmn/session/").then (resp) ->
    #$http.get("/api/lmn/session/sessions").then (username,session) ->
                #$http.post('/api/lmn/session/sessions', {action: 'get-participants', username: username, session: session}).then (resp) ->
                    #$scope.sessions = resp.data
                #$scope.sessions = resp.data


