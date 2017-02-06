angular.module('lm.rooms').config ($routeProvider) ->
    $routeProvider.when '/view/lm/room-defaults',
        controller: 'LMRoomDefaultsController'
        templateUrl: '/lm_rooms:resources/partial/index.html'


angular.module('lm.rooms').controller 'LMRoomDefaultsApplyModalController', ($scope, $http, $uibModalInstance, gettext, notify) ->
    $scope.logVisible = false
    $scope.isWorking = true
    $scope.showLog = () ->
        $scope.logVisible = true

    $http.get('/api/lm/room-defaults/apply').then () ->
        $scope.isWorking = false
        notify.success gettext('Update complete')
    .catch (resp) ->
        notify.error gettext('Update failed'), resp.data.message
        $scope.isWorking = false
        $scope.showLog()

    $scope.close = () ->
        $uibModalInstance.close()


angular.module('lm.rooms').controller 'LMRoomDefaultsController', ($scope, $http, $uibModal, $q, gettext, notify, pageTitle, lmFileBackups) ->
    pageTitle.set(gettext('Rooms'))

    $http.get('/api/lm/workstations').then (resp) ->
        $scope.rooms = []
        knownRooms = []
        $scope.newObjects = []
        $scope.workstations = resp.data
        for w in $scope.workstations
            if w.room not in knownRooms and w.room[0] != '#' and w.room
                $scope.newObjects.push w.room
                $scope.rooms.push {name: w.room}
                knownRooms.push w.room

        for w in $scope.workstations
            $scope.newObjects.push w.hostname

        $http.get('/api/lm/edv-rooms').then (resp) ->
            edvRooms = resp.data
            for room in $scope.rooms
                room.edv =  room.name in edvRooms

    $http.get('/api/lm/room-defaults').then (resp) ->
        $scope.defaults = resp.data


    $scope.add = (id) ->
        d = angular.copy($scope.defaults[0])
        d.id = id
        $scope.defaults.push d

    $scope.reset = (d) ->
        for k in ['internet', 'intranet', 'webfilter']
            d[k] = $scope.defaults[0][k]

    $scope.remove = (d) ->
        $scope.defaults.remove(d)

    $scope.save = () ->
        edvRooms = (x.name for x in $scope.rooms when x.edv)
        return $q.all([
            $http.post('/api/lm/room-defaults', $scope.defaults)
            $http.post('/api/lm/edv-rooms', edvRooms)
        ]).then () ->
            notify.success gettext('Saved')

    $scope.apply = () ->
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lm_rooms:resources/partial/apply.modal.html'
                controller: 'LMRoomDefaultsApplyModalController'
                backdrop: 'static'
            )

    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/room_defaults')
