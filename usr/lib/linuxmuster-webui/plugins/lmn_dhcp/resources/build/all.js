'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('lmn.dhcp', ['core', 'lmn.common', 'lmn.devices']);


'use strict';

angular.module('lmn.dhcp').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/dhcp', {
        templateUrl: '/lmn_dhcp:resources/partial/index.html',
        controller: 'ExtraDhcpIndexController'
    });
});


'use strict';

angular.module('lmn.dhcp').controller('ExtraDhcpIndexController', function ($scope, $http, pageTitle, gettext, notify, $uibModal) {
    pageTitle.set(gettext('DHCP'));

    $http.get('/api/lmn/dhcp/leases').then(function (resp) {
        $scope.leases = resp.data[0];
        $scope.used = resp.data[1];
    });

    $scope.alreadyIn = function (mac) {
        var _iteratorNormalCompletion = true;
        var _didIteratorError = false;
        var _iteratorError = undefined;

        try {
            for (var _iterator = $scope.used[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                device = _step.value;

                if (device.mac) {
                    if (device.mac.toUpperCase() == mac.toUpperCase()) return true;
                }
            }
        } catch (err) {
            _didIteratorError = true;
            _iteratorError = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion && _iterator.return) {
                    _iterator.return();
                }
            } finally {
                if (_didIteratorError) {
                    throw _iteratorError;
                }
            }
        }

        return false;
    };

    $scope.addDevice = function (device) {
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
            sophomorixComment: ''
        };

        $uibModal.open({
            templateUrl: '/lmn_dhcp:resources/partial/addDevice.modal.html',
            controller: 'ExtraDhcpAddController',
            size: 'mg',
            scope: $scope // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        });
    };
});

angular.module('lmn.dhcp').controller('ExtraDhcpAddController', function ($scope, $http, pageTitle, gettext, notify, validation, $uibModalInstance, $uibModal) {

    // Register devices in validation service to test for duplicate
    validation.set($scope.used, 'devices');

    $scope.duplicateIP = function () {
        var _iteratorNormalCompletion2 = true;
        var _didIteratorError2 = false;
        var _iteratorError2 = undefined;

        try {
            for (var _iterator2 = $scope.used[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                device = _step2.value;

                if (device.ip == $scope.newDevice.ip) return true;
            }
        } catch (err) {
            _didIteratorError2 = true;
            _iteratorError2 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion2 && _iterator2.return) {
                    _iterator2.return();
                }
            } finally {
                if (_didIteratorError2) {
                    throw _iteratorError2;
                }
            }
        }

        return false;
    };
    $scope.duplicateHost = function () {
        var _iteratorNormalCompletion3 = true;
        var _didIteratorError3 = false;
        var _iteratorError3 = undefined;

        try {
            for (var _iterator3 = $scope.used[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
                device = _step3.value;

                if (device.hostname == $scope.newDevice.hostname) return true;
            }
        } catch (err) {
            _didIteratorError3 = true;
            _iteratorError3 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion3 && _iterator3.return) {
                    _iterator3.return();
                }
            } finally {
                if (_didIteratorError3) {
                    throw _iteratorError3;
                }
            }
        }

        return false;
    };
    $scope.save = function () {
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
        $http.post('/api/lmn/dhcp/register', { device: $scope.newDevice }).then(function () {
            notify.success(gettext('Device successfully saved in devices.csv!'));
            $scope.used.push({
                'mac': device.mac,
                'ip': device.ip,
                'hostname': device.hostname
            });
            $scope.close();
        });
    };

    $scope.saveImport = function () {
        $scope.save();
        $uibModal.open({
            templateUrl: '/lmn_devices:resources/partial/apply.modal.html',
            controller: 'LMDevicesApplyModalController',
            size: 'lg',
            backdrop: 'static'
        });
    };

    $scope.close = function () {
        $uibModalInstance.close();
    };
});


