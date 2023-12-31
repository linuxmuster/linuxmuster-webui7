angular.module('lmn.session_new').controller 'LMNSessionsListController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap, filesystem, validation, $rootScope, wait, lmnSession) ->
    pageTitle.set(gettext('Sessions list'))

    $scope.startSchoolclassSessionMouseover = gettext('Start this session with all student in this schoolclass')
    $scope.generateRoomSessionMouseover = gettext('Start session containing all users in this room')
    $scope.loading = true

    $http.get('/api/lmn/session/userInRoom').then (resp) ->
        $scope.room = resp.data
        $scope.loading = false

    $scope.renameSession = (session, e) ->
        e.stopPropagation()
        lmnSession.rename(session.sid, session.name).then (resp) ->
            session.name = resp

    $scope.killSession = (session, e) ->
        e.stopPropagation()
        lmnSession.kill(session.sid, session.name).then () ->
            position = $scope.sessions.indexOf(session)
            $scope.sessions.splice(position, 1)

    $scope.cloneSession = (session, e) ->
        e.stopPropagation()
        lmnSession.new(session.members).then () ->
            $scope.getSessions()

    $scope.newSession = () ->
        lmnSession.new().then () ->
            $scope.getSessions()

    $scope.getSessions = () ->
        lmnSession.load().then (resp) ->
            $scope.schoolclasses = resp[0]
            $scope.projects = resp[1]
            $scope.sessions = resp[2]

    $scope.start = (session) ->
        lmnSession.reset()
        lmnSession.start(session)

    $scope.startGenerated = (group) ->
        lmnSession.reset()
        if group == 'this_room'
            $http.post("/api/lmn/session/userinfo", {users:$scope.room.usersList}).then (resp) ->
                lmnSession.startGenerated($scope.room.name, resp.data, 'room')
        else
            # get participants from specified class or project
            $http.post("/api/lmn/session/userinfo", {users:group.members}).then (resp) ->
                lmnSession.startGenerated(group.name, resp.data, group.type)

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
            return
        if $scope.identity.user is null
            return
        if $scope.identity.user is 'root'
            return
        $scope.getSessions()
