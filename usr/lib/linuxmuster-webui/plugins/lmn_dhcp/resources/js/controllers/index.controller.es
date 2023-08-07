angular.module('lmn.dhcp').controller('ExtraDhcpIndexController', function($scope, $http, pageTitle, gettext, notify, $uibModal) {
    pageTitle.set(gettext('DHCP'));

    $http.get('/api/lmn/dhcp/leases').then( (resp) => {
	    $scope.leases = resp.data[0];
        $scope.used = resp.data[1];
    });

    $scope.alreadyIn = (mac) => {
        for (device of $scope.used) {
            if (device.mac) {
                if (device.mac.toUpperCase() == mac.toUpperCase()) return true;
            }
        }
        return false;
    }

    $scope.addDevice = (device) => {
        $scope.newDevice = {
            room: '',
            hostname: '',
            group: '',
            mac: device.mac,
            ip: '',
            pxeFlag: '0',
            officeKey: '',
            windowsKey: '',
            dhcpOptions: '',
            sophomorixRole: 'staffcomputer',
            lmnReserved10: '',
            lmnReserved12: '',
            lmnReserved13: '',
            lmnReserved14: '',
            sophomorixComment: '',
        }

        $uibModal.open({
            templateUrl: '/lmn_dhcp:resources/partial/addDevice.modal.html',
            controller: 'ExtraDhcpAddController',
            size: 'mg',
            scope: $scope, // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        });
    }
});

angular.module('lmn.dhcp').controller('ExtraDhcpAddController', function($scope, $http, pageTitle, gettext, notify, validation, $uibModalInstance, $uibModal) {

    // Register devices in validation service to test for duplicate
    validation.set($scope.used, 'devices');

    $scope.duplicateIP = () => {
        for (device of $scope.used) {
            if (device.ip == $scope.newDevice.ip) return true;
        }
        return false;
    }
    $scope.duplicateHost = () => {
        for (device of $scope.used) {
            if (device.hostname == $scope.newDevice.hostname) return true;
        }
        return false;
    }
    $scope.save = () => {
        $scope.formNotValid = false;
        testIP = validation.isValidIP($scope.newDevice.ip);
        if (testIP != true) {
            notify.error(testIP);
            $scope.formNotValid = true;
        }
        testHost = validation.isValidHost($scope.newDevice.hostname);
        if (testHost != true) {
            notify.error(testHost);
            $scope.formNotValid = true;
        }
        if ($scope.formNotValid) {
            return;
        }
        $scope.formNotValid = false;
        $http.post('/api/lmn/dhcp/register', {device: $scope.newDevice}).then( () => {
            notify.success(gettext('Device successfully saved in devices.csv!'));
            $scope.used.push({
                'mac': device.mac,
                'ip': device.ip,
                'hostname': device.hostname,
            });
            $scope.close();
        });
    }

    $scope.saveImport = () => {
        $scope.save();
        $uibModal.open({
            templateUrl: '/lmn_devices:resources/partial/apply.modal.html',
            controller: 'LMDevicesApplyModalController',
            size: 'lg',
            backdrop: 'static',
        });
    }

    $scope.close = () => {
        $uibModalInstance.close();
    }
});
