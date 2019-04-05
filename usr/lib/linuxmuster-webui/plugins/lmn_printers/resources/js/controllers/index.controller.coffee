angular.module('lm.printers').config ($routeProvider) ->
    $routeProvider.when '/view/lm/printers',
        controller: 'LMPrintersController'
        templateUrl: '/lmn_printers:resources/partial/index.html'


angular.module('lm.printers').controller 'LMPrintersModalController', ($scope, $uibModalInstance, workstationIPs, roomSubnets, printer) ->
    $scope.printer = printer
    newWorkstations = (k for k,v of workstationIPs)
    newWorkstations.sort()
    newSubnets = (k for k,v of roomSubnets)
    newSubnets.sort()
    $scope.newObjects = newSubnets.concat(newWorkstations)

    $scope.add = (item) ->
        printer.items.push item

    $scope.save = () ->
        $uibModalInstance.close(printer)

    $scope.close = () ->
        $uibModalInstance.dismiss()


angular.module('lm.printers').controller 'LMPrintersController', ($scope, $http, $uibModal, $log, gettext, notify, pageTitle, lmFileBackups) ->
    pageTitle.set(gettext('Printers'))

    $http.get('/api/lm/devices').then (resp) ->
        $scope.workstationIPs = {}
        $scope.roomSubnets = {}

        for workstation in resp.data
            if workstation.ip
                $scope.workstationIPs[workstation.hostname] = workstation.ip

                subnet = workstation.ip.slice(0, workstation.ip.lastIndexOf('.')) + '.*'
                $scope.roomSubnets[workstation.room] ?= []
                if subnet not in $scope.roomSubnets[workstation.room]
                    $scope.roomSubnets[workstation.room].push subnet

        $http.get('/api/lm/printers').then (resp) ->
            printers = resp.data
            mappedPrinters = {}

            for printer in printers
                mappedPrinters[printer.name] = []

                for name, ip of $scope.workstationIPs
                    if ip in printer.items
                        if name not in mappedPrinters[printer.name].push
                            mappedPrinters[printer.name].push name

                for name, subnets of $scope.roomSubnets
                    for subnet in subnets
                        if subnet in printer.items
                            if name not in mappedPrinters[printer.name].push
                                mappedPrinters[printer.name].push name

            $scope.printers = ({name: k, items: v} for k,v of mappedPrinters)
            $log.log 'Mapped printers', $scope.printers

    $scope.edit = (printer) ->
        $uibModal.open(
            templateUrl: '/lmn_printers:resources/partial/printer.modal.html'
            controller: 'LMPrintersModalController'
            resolve:
                workstationIPs: () -> $scope.workstationIPs
                roomSubnets: () -> $scope.roomSubnets
                printer: () -> angular.copy(printer)
        ).result.then (result) ->
            angular.copy(result, printer)
            $scope.save()

    $scope.save = () ->
        printers = []
        for printer in $scope.printers
            unmappedPrinter = {
                name: printer.name
                items: []
            }
            printers.push unmappedPrinter
            for item in printer.items
                if $scope.workstationIPs[item]
                    unmappedPrinter.items.push $scope.workstationIPs[item]
                if $scope.roomSubnets[item]
                    for subnet in $scope.roomSubnets[item]
                        unmappedPrinter.items.push subnet

        $http.post('/api/lm/printers', printers).then () ->
            notify.success gettext('Saved')

    $scope.backups = () ->
        lmFileBackups.show('/etc/cups/access.conf')
