angular.module('lm.workstations').config ($routeProvider) ->
    $routeProvider.when '/view/lm/workstations',
        controller: 'LMWorkstationsController'
        templateUrl: '/lm_workstations:resources/partial/index.html'


angular.module('lm.workstations').controller 'LMWorkstationsApplyModalController', ($scope, $http, $uibModalInstance, gettext, notify) ->
    $scope.logVisible = false
    $scope.isWorking = true
    $scope.showLog = () ->
        $scope.logVisible = true

    $http.get('/api/lm/workstations/import').then (resp) ->
        $scope.isWorking = false
        notify.success gettext('Import complete')
    .catch (resp) ->
        notify.error gettext('Import failed'), resp.data.message
        $scope.isWorking = false
        $scope.showLog()

    $scope.close = () ->
        $uibModalInstance.close()



angular.module('lm.workstations').controller 'LMWorkstationsController', ($scope, $http, $uibModal, $route, gettext, notify, pageTitle, lmFileEditor, lmFileBackups) ->
    pageTitle.set(gettext('Workstations'))

    $scope.sorts = [
        {
            name: gettext('Room')
            fx: (x) -> x.room
        }
        {
            name: gettext('Group')
            fx: (x) -> x.group
        }
        {
            name: gettext('Hostname')
            fx: (x) -> x.hostname
        }
        {
            name: gettext('MAC')
            fx: (x) -> x.mac
        }
        {
            name: gettext('IP')
            fx: (x) -> x.ip
        }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
        page: 1
        pageSize: 100

    $scope.stripComments = (value) -> !value.room or value.room[0] != '#'

    $scope.add = () ->
        $scope.paging.page = Math.floor(($scope.workstations.length - 1) / $scope.paging.pageSize) + 1
        $scope.filter = ''
        $scope.workstations.push {
            _isNew: true
            accountType: '1',
            pxeFlag: '1',
        }

    $scope.fields = {
        room:
            visible: true
            name: gettext('Room')
        hostname:
            visible: true
            name: gettext('Hostname')
        group:
            visible: true
            name: gettext('Group')
        mac:
            visible: true
            name: gettext('MAC')
        ip:
            visible: true
            name: gettext('IP')
        officeKey:
            visible: false
            name: gettext('Office Key')
        windowsKey:
            visible: false
            name: gettext('Windows Key')
        userReserved:
            visible: false
            name: gettext('User-defined')
        accountType:
            visible: false
            name: gettext('Account type')
        pxeFlag:
            visible: true
            name: gettext('PXE')
    }

    $http.get('/api/lm/workstations').then (resp) ->
        $scope.workstations = resp.data

    $scope.remove = (workstation) ->
        $scope.workstations.remove(workstation)

    $scope.save = () ->
        return $http.post('/api/lm/workstations', $scope.workstations).then () ->
            notify.success gettext('Saved')

    $scope.saveAndImport = () ->
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lm_workstations:resources/partial/apply.modal.html'
                controller: 'LMWorkstationsApplyModalController'
                backdrop: 'static'
            )

    $scope.editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/devices.csv').then () ->
            $route.reload()

    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/devices.csv')
