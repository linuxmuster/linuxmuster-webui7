angular.module('lmn.session').controller 'LMNSessionsListController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap, filesystem, validation, $rootScope, wait, lmnSession) ->
    pageTitle.set(gettext('Sessions list'))

    $scope.generateSessionMouseover = gettext('Regenerate this session')
    $scope.startGeneratedSessionMouseover = gettext('Start this session unchanged (may not be up to date)')
    $scope.generateRoomsessionMouseover = gettext('Start session containing all users in this room')

    $scope.checkboxModel = {
       value1 : false,
       value2 : true
    }

    $scope.visible = {
       participanttable : 'none',
       sessiontable : 'none',
       sessionname : 'none',
       mainpage: 'show',
    }


    $scope.info = {
        message : ''
    }

    $scope._ = {
            addParticipant: null,
            addClass: null
    }

    $scope.room = {
        "usersList": [],
        'name': '',
        'objects': {},
    }
    $http.get('/api/lmn/session/userInRoom').then (resp) ->
        if resp.data != 0
            $scope.room = resp.data

    $scope.resetClass = () ->
        result = document.getElementsByClassName("changed")
        while result.length
            result[0].className = result[0].className.replace( /(?:^|\s)changed(?!\S)/g , '' )
        return

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

    $scope.showGroupDetails = (index, groupType, groupName) ->
       $uibModal.open(
          templateUrl: '/lmn_groupmembership:resources/partial/groupDetails.modal.html'
          controller:  'LMNGroupDetailsController'
          size: 'lg'
          resolve:
            groupType: () -> groupType
            groupName: () -> groupName
       )

    $scope.start = (session) ->
        lmnSession.start(session)

    $scope.startGroup = (groupname) ->
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

angular.module('lmn.session').controller 'LMNRoomDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, usersInRoom) ->
        $scope.usersInRoom = usersInRoom

        $scope.close = () ->
            $uibModalInstance.dismiss()