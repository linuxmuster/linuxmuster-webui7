'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('lmn.unifi', ['core']);


'use strict';

angular.module('lmn.unifi').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/unifi', {
        templateUrl: '/lmn_unifi:resources/partial/index.html',
        controller: 'LMN_unifiIndexController'
    });
});


'use strict';

angular.module('lmn.unifi').controller('LMN_unifiIndexController', function ($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Unifi'));

    $scope.paging = {
        page: 1,
        pageSize: 10
    };

    $scope.query = "";

    $scope.refresh = function () {
        $scope.deviceList = [];
        $scope.start();
    };

    $scope.rebootAP = function (device) {
        $http.post('/api/lmn/unifi/rebootDevice', { device: device }).then(function (resp) {
            console.log(resp.data);
            if (resp.data.status == "success") {
                notify.success("AP " + device.DEVICE_NAME + " reboot initiated!");
                $scope.start();
            } else {
                notify.error("Could not initiate reboot for " + device.DEVICE_NAME + "! - " + resp.data.data);
            }
        });
    };

    $scope.enableAP = function (device) {
        $http.post('/api/lmn/unifi/enableDevice', { device: device }).then(function (resp) {
            console.log(resp.data);
            if (resp.data.status == "success") {
                notify.success("AP " + device.DEVICE_NAME + " successful enabled!");
                $scope.start();
            } else {
                notify.error("Could not enable " + device.DEVICE_NAME + "!");
            }
        });
    };

    $scope.disableAP = function (device) {
        $http.post('/api/lmn/unifi/disableDevice', { device: device }).then(function (resp) {
            console.log(resp.data);
            if (resp.data.status == "success") {
                notify.success("AP " + device.DEVICE_NAME + " successful disabled!");
                $scope.start();
            } else {
                notify.error("Could not disable " + device.DEVICE_NAME + "!");
            }
        });
    };

    $scope.toggleAPState = function (device) {
        if (device.DISABLED == "0") {
            $scope.disableAP(device);
        } else {
            $scope.enableAP(device);
        }
    };

    $scope.batchRebootAP = function () {
        if ($scope.deviceList) {
            var _iteratorNormalCompletion = true;
            var _didIteratorError = false;
            var _iteratorError = undefined;

            try {
                for (var _iterator = $scope.deviceList[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                    var device = _step.value;

                    if (device.selected) {
                        $scope.rebootAP(device);
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
        }
    };

    $scope.batchDisableAP = function () {
        if ($scope.deviceList) {
            var _iteratorNormalCompletion2 = true;
            var _didIteratorError2 = false;
            var _iteratorError2 = undefined;

            try {
                for (var _iterator2 = $scope.deviceList[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                    var device = _step2.value;

                    if (device.selected) {
                        $scope.disableAP(device);
                    }
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
        }
    };

    $scope.batchEnableAP = function () {
        if ($scope.deviceList) {
            var _iteratorNormalCompletion3 = true;
            var _didIteratorError3 = false;
            var _iteratorError3 = undefined;

            try {
                for (var _iterator3 = $scope.deviceList[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
                    var device = _step3.value;

                    if (device.selected) {
                        $scope.enableAP(device);
                    }
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
        }
    };

    $scope.start = function () {
        $http.get('/api/lmn/unifi/getDevices').then(function (resp) {
            if (resp.data.status == "success") {
                console.log(resp.data.data);
                $scope.deviceList = resp.data.data;
            } else {
                console.log("Error!");
            }
        });
        // setTimeout(function() {
        //     $scope.start();
        // }, 10000);
    };

    $scope.filter = function (item) {
        var _arr = ["DEVICE_NAME", "DEVICE_IP", "DEVICE_MAC"];

        for (var _i = 0; _i < _arr.length; _i++) {
            var value = _arr[_i];
            if (item[value].toLowerCase().includes($scope.query.toLowerCase())) {
                return true;
            }
        }
        return false;
    };

    $scope.selectAll = function () {
        var newdeviceList = [];
        var _iteratorNormalCompletion4 = true;
        var _didIteratorError4 = false;
        var _iteratorError4 = undefined;

        try {
            for (var _iterator4 = $scope.deviceList[Symbol.iterator](), _step4; !(_iteratorNormalCompletion4 = (_step4 = _iterator4.next()).done); _iteratorNormalCompletion4 = true) {
                var device = _step4.value;

                if ($scope.all_selected) {
                    if ($scope.filter(device)) {
                        if (device.selected) {
                            device.selected = false;
                        } else {
                            device.selected = true;
                        }
                    }
                } else {
                    device.selected = false;
                }
                newdeviceList.push(device);
            }
        } catch (err) {
            _didIteratorError4 = true;
            _iteratorError4 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion4 && _iterator4.return) {
                    _iterator4.return();
                }
            } finally {
                if (_didIteratorError4) {
                    throw _iteratorError4;
                }
            }
        }

        $scope.deviceList = newdeviceList;
    };

    $scope.haveSelection = function () {
        if ($scope.deviceList) {
            var _iteratorNormalCompletion5 = true;
            var _didIteratorError5 = false;
            var _iteratorError5 = undefined;

            try {
                for (var _iterator5 = $scope.deviceList[Symbol.iterator](), _step5; !(_iteratorNormalCompletion5 = (_step5 = _iterator5.next()).done); _iteratorNormalCompletion5 = true) {
                    var device = _step5.value;

                    if (device.selected) {
                        return true;
                    }
                }
            } catch (err) {
                _didIteratorError5 = true;
                _iteratorError5 = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion5 && _iterator5.return) {
                        _iterator5.return();
                    }
                } finally {
                    if (_didIteratorError5) {
                        throw _iteratorError5;
                    }
                }
            }
        }
        return false;
    };

    $scope.$watch('identity.user', function () {
        if ($scope.identity.user == undefined) {
            return;
        }
        if ($scope.identity.user == null) {
            return;
        }

        $scope.user = $scope.identity.profile;
        $scope.start();
    });
});


