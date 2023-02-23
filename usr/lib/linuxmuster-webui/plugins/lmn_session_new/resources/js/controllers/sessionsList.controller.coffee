angular.module('lmn.session_new').controller 'LMNSessionsListController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap, filesystem, validation, $rootScope, wait, lmnSession) ->
    pageTitle.set(gettext('Sessions list'))

    $scope.generateSessionMouseover = gettext('Regenerate this session')
    $scope.startGeneratedSessionMouseover = gettext('Start this session unchanged (may not be up to date)')
    $scope.generateRoomsessionMouseover = gettext('Start session containing all users in this room')
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
        lmnSession.rename(session.ID, session.COMMENT).then (resp) ->
            session.COMMENT = resp

    $scope.killSession = (session) ->
        lmnSession.kill(session.ID, session.COMMENT).then () ->
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
        lmnSession.start(session)

    $scope.startGenerated = (groupname) ->
        if groupname == 'this_room'
            $http.post("/api/lmn/session/userinfo", {users:$scope.room.usersList}).then (resp) ->
                lmnSession.startGenerated('this_room', resp.data)
        else
            $http.get("/api/lmn/session/group/#{groupname}").then (resp) ->
                # get participants from specified class
                lmnSession.startGenerated(groupname, resp.data)

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