angular.module('lmn.session_new').controller 'LMNSessionsListController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap, filesystem, validation, $rootScope, wait, lmnSession) ->
    pageTitle.set(gettext('Sessions list'))

    $scope.startSchoolclassSessionMouseover = gettext('Start this session with all student in this schoolclass')
    $scope.generateRoomSessionMouseover = gettext('Start session containing all users in this room')
    $scope.loading = true

    $scope.room = {
        "usersList": [],
        'name': '',
        'objects': {},
    }

    $http.get('/api/lmn/session/userInRoom').then (resp) ->
        if resp.data != 0
            $scope.room = resp.data
        $scope.loading = false

    $scope.renameSession = (session) ->
        lmnSession.rename(session.sid, session.name).then (resp) ->
            session.name = resp

    $scope.killSession = (session) ->
        lmnSession.kill(session.sid, session.name).then () ->
            position = $scope.sessions.indexOf(session)
            $scope.sessions.splice(position, 1)

    $scope.newSession = () ->
        lmnSession.new().then () ->
            $scope.getSessions()

    $scope.getSessions = () ->
        lmnSession.load().then (resp) ->
            $scope.classes = resp[0]
            $scope.sessions = resp[1]

    $scope.start = (session) ->
        lmnSession.reset()
        lmnSession.start(session)

    $scope.startGenerated = (groupname) ->
        lmnSession.reset()
        if groupname == 'this_room'
            $http.post("/api/lmn/session/userinfo", {users:$scope.room.usersList}).then (resp) ->
                lmnSession.startGenerated($scope.room.name, resp.data, 'room')
        else
            $http.get("/api/lmn/session/group/#{groupname}").then (resp) ->
                # get participants from specified class
                lmnSession.startGenerated(groupname, resp.data, 'schoolclass')

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
            return
        if $scope.identity.user is null
            return
        if $scope.identity.user is 'root'
            return
        $scope.getSessions()

#angular.module('lmn.session_new').controller 'LMNRoomDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, usersInRoom) ->
#        $scope.usersInRoom = usersInRoom
#
#        $scope.close = () ->
#            $uibModalInstance.dismiss()