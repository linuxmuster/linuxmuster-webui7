angular.module('lm.devices').config ($routeProvider) ->
    $routeProvider.when '/view/lm/devices',
        controller: 'LMDevicesController'
        templateUrl: '/lmn_devices:resources/partial/index.html'


angular.module('lm.devices').controller 'LMDevicesApplyModalController', ($scope, $http, $uibModalInstance, gettext, notify) ->
    $scope.logVisible = true
    $scope.isWorking = true
    $scope.showLog = () ->
        $scope.logVisible = !$scope.logVisible

    $http.get('/api/lm/devices/import').then (resp) ->
        $scope.isWorking = false
        notify.success gettext('Import complete')
    .catch (resp) ->
        notify.error gettext('Import failed'), resp.data.message
        $scope.isWorking = false
        $scope.showLog()

    $scope.close = () ->
        $uibModalInstance.close()



angular.module('lm.devices').controller 'LMDevicesController', ($scope, $http, $uibModal, $route, $location, $anchorScroll, gettext, notify, pageTitle, lmFileEditor, lmFileBackups, validation) ->
    pageTitle.set(gettext('Devices'))

    $scope.error_msg = {}
    $scope.show_errors = false
    $scope.emptyCells = {}
    $scope.first_save = false
    $scope.trans ={
        duplicate: gettext('Duplicate')
        remove:  gettext('Remove')
    }

    $scope.$on("$locationChangeStart", (event) ->
        if ($scope.devices_form.$dirty && !confirm(gettext('Changes are not saved, continue anyway ?')))
            event.preventDefault()
        )

    $scope.dictLen = (d) ->
        return Object.keys(d).length

    $scope.validateField = (name, val, isnew, ev) ->
        test = validation["isValid"+name](val)

        if test == true && (val || name == "Comment")
            delete $scope.error_msg[name+"-"+ev]
            delete $scope.emptyCells[name+"-"+ev]
            return ""
        else if !val
            delete $scope.error_msg[name+"-"+ev]
            $scope.emptyCells[name+"-"+ev] = 1
        else
            delete $scope.emptyCells[name+"-"+ev]
            if Object.values($scope.error_msg).indexOf(test) == -1
                $scope.error_msg[name+"-"+ev] = test

        return "has-error-new"

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

    $scope.stripComments = (value) -> value.room and value.room[0] != '#'

    $scope.add = () ->
        if $scope.devices.length > 0
            $scope.paging.page = Math.floor(($scope.devices.length - 1) / $scope.paging.pageSize) + 1
        $scope.filter = ''
        $scope.devices.push {
            _isNew: true,
            room: '',
            hostname: '',
            group: '',
            mac: '',
            ip: '',
            sophomorixRole: 'classroom-studentcomputer',
            pxeFlag: '1',
        }

    $scope.duplicate = (device) ->
        $scope.devices.push {
            _isNew: true
            room: device.room,
            hostname: device.hostname,
            group: device.group,
            mac: device.mac,
            ip: device.ip,
            officeKey: device.officeKey,
            windowsKey: device.windowsKey,
            dhcpOptions: device.dhcpOptions,
            sophomorixRole: device.sophomorixRole,
            lmnReserved10: device.lmnReserved10,
            pxeFlag: device.pxeFlag,
            lmnReserved12: device.lmnReserved12,
            lmnReserved13: device.lmnReserved13,
            lmnReserved14: device.lmnReserved14,
            sophomorixComment: device.sophomorixComment,
        }
        $location.hash('end_table');
        $anchorScroll();

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
        dhcpOptions:
            visible: false
            name: gettext('DHCP-Options')
        sophomorixRole:
            visible: true
            name: gettext('Sophomorix-Role')
        lmnReserved10:
            visible: false
            name: gettext('LMN-Reserved 10')
        pxeFlag:
            visible: true
            name: gettext('PXE')
        lmnReserved12:
            visible: false
            name: gettext('LMN-Reserved 12')
        lmnReserved13:
            visible: false
            name: gettext('LMN-Reserved 13')
        lmnReserved14:
            visible: false
            name: gettext('LMN-Reserved 14')
        sophomorixComment:
            visible: false
            name: gettext('Sophomorix-Comment')
    }

    $http.get('/api/lm/devices').then (resp) ->
        $scope.devices = resp.data
        validation.set($scope.devices, 'devices')

    $scope.remove = (device) ->
        $scope.devices.remove(device)

    $scope.numErrors = () ->
        # Remove previous errors
        angular.element(document.getElementsByClassName("has-error")).removeClass('has-error')
        return document.getElementsByClassName("has-error-new").length > 0

    $scope.save = () ->
        if $scope.numErrors()
            $scope.first_save = true
            $scope.show_errors = true
            angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
            notify.error(gettext('Please check the errors.'))
            return
        $scope.show_errors = false
        $scope.devices_form.$setPristine()
        return $http.post('/api/lm/devices', $scope.devices).then () ->
            notify.success gettext('Saved')

    $scope.saveAndImport = () ->
        if $scope.numErrors()
            $scope.first_save = true
            $scope.show_errors = true
            angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
            notify.error(gettext('Please check the errors.'))
            return
        $scope.show_errors = false
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lmn_devices:resources/partial/apply.modal.html'
                controller: 'LMDevicesApplyModalController'
                size: 'lg'

                backdrop: 'static'
            )

    $scope.path = '/etc/linuxmuster/sophomorix/default-school/devices.csv'

    $scope.editCSV = () ->
        lmFileEditor.show($scope.path).then () ->
            $route.reload()

    $scope.backups = () ->
        lmFileBackups.show($scope.path)        
