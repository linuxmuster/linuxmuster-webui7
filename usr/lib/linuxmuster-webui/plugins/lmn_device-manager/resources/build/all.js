'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('lmn.device-manager', ['core']);


'use strict';

angular.module('lmn.device-manager').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/device-manager', {
        templateUrl: '/lmn.device-manager:resources/partial/index.html',
        controller: 'LMP_DeviceManagerIndexController'
    });
});


'use strict';

angular.module('lmn.device-manager').controller('LMP_DeviceManagerIndexController', function ($scope, $http, pageTitle, gettext, notify, $uibModal) {
    pageTitle.set(gettext('Device Manager'));

    $scope.start = function () {
        $scope.allDevicesSelected = false;
        $scope.deviceListFilteredChecked = [];
        $scope.runningLinboRemoteCommands = [];
        $scope.preStartCommands = [];

        $http.get('/api/lmn/activeschool').then(function (resp) {
            $scope.identity.profile.activeSchool = resp.data;
            var school = $scope.identity.profile.activeSchool;

            if (school == "default-school") {
                $scope.path = '/etc/linuxmuster/sophomorix/default-school/devices.csv';
            } else {
                $scope.path = '/etc/linuxmuster/sophomorix/' + school + '/' + school + '.devices.csv';
            }

            $http.post('/api/lmn/device-manager/getdevices', { filepath: $scope.path, school: school }).then(function (resp) {
                $scope.deviceList = resp.data;
                $scope.deviceListFiltered = [];
                $scope.createRoomList();
                $scope.checkStatus();
            });
        });
        $scope.autoRefreshStatus = false;
        $scope.autoRefreshStatusTimerStart = 30;
        $scope.autoRefreshStatusTimerCurrent = $scope.autoRefreshStatusTimerStart;
        setInterval(function () {
            if ($scope.autoRefreshStatus && $scope.deviceListFiltered.length > 0) {
                if ($scope.autoRefreshStatusTimerCurrent == 0) {
                    $scope.checkStatus();
                    $scope.autoRefreshStatusTimerCurrent = $scope.autoRefreshStatusTimerStart;
                } else {
                    $scope.autoRefreshStatusTimerCurrent = $scope.autoRefreshStatusTimerCurrent - 1;
                }
            }
        }, 1000);
    };

    $scope.getRunningLinboRemoteCommands = function () {
        $http.get('/api/lmn/device-manager/getrunninglinboremotecommands').then(function (resp) {
            console.log(resp.data);
            $scope.runningLinboRemoteCommands = resp.data;
        });
    };

    $scope.getPrestartCommands = function () {
        $http.get('/api/lmn/device-manager/getPrestartCommands').then(function (resp) {
            $scope.preStartCommands = resp.data;
        });
    };

    $scope.createRoomList = function () {
        $scope.roomList = {};
        var _iteratorNormalCompletion = true;
        var _didIteratorError = false;
        var _iteratorError = undefined;

        try {
            for (var _iterator = $scope.deviceList[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                var device = _step.value;

                if (!(device.room in $scope.roomList)) {
                    $scope.roomList[device.room] = { "name": device.room, "checked": false };
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
    };

    $scope.getSelectedRooms = function () {
        $scope.selectedRooms = [];
        for (var room in $scope.roomList) {
            if ($scope.roomList[room].checked) {
                $scope.selectedRooms.push($scope.roomList[room].name);
            }
        }
    };

    $scope.refreshDeviceListFiltered = function () {
        $scope.getSelectedRooms();
        $scope.deviceListFiltered = [];
        for (var device in $scope.deviceList) {
            var _iteratorNormalCompletion2 = true;
            var _didIteratorError2 = false;
            var _iteratorError2 = undefined;

            try {
                for (var _iterator2 = $scope.selectedRooms[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                    var room = _step2.value;

                    if (room == $scope.deviceList[device].room) {
                        $scope.deviceListFiltered.push($scope.deviceList[device]);
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
        $scope.checkStatus();
    };

    $scope.checkStatus = function () {
        $scope.checkOnline();
        $scope.checkOS();
        $scope.getRunningLinboRemoteCommands();
        $scope.getPrestartCommands();
    };

    $scope.checkOnline = function () {
        var _iteratorNormalCompletion3 = true;
        var _didIteratorError3 = false;
        var _iteratorError3 = undefined;

        try {
            var _loop = function _loop() {
                var device = _step3.value;

                $http.post('/api/lmn/device-manager/checkOnline', { device: device }).then(function (resp) {
                    device.online = resp.data;
                });
            };

            for (var _iterator3 = $scope.deviceListFiltered[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
                _loop();
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
    };

    $scope.checkOS = function () {
        var _iteratorNormalCompletion4 = true;
        var _didIteratorError4 = false;
        var _iteratorError4 = undefined;

        try {
            var _loop2 = function _loop2() {
                var device = _step4.value;

                $http.post('/api/lmn/device-manager/checkOS', { device: device }).then(function (resp) {
                    device.os = resp.data;
                });
            };

            for (var _iterator4 = $scope.deviceListFiltered[Symbol.iterator](), _step4; !(_iteratorNormalCompletion4 = (_step4 = _iterator4.next()).done); _iteratorNormalCompletion4 = true) {
                _loop2();
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
    };

    $scope.deviceShutdown = function (device) {
        $http.post('/api/lmn/device-manager/shutdown', { device: device }).then(function (resp) {
            notify.success(gettext('Device shutdown successful initiated!'));
            setTimeout(function () {
                $scope.checkStatus();
            }, 3000);
        }, function (error) {
            console.log('Device shutdown failed!', error);
            notify.error(gettext('Device shutdown failed!'));
        });
    };

    $scope.deviceReboot = function (device) {
        $http.post('/api/lmn/device-manager/reboot', { device: device }).then(function (resp) {
            notify.success(gettext('Device reboot successful initiated!'));
            setTimeout(function () {
                $scope.checkStatus();
            }, 3000);
        }, function (error) {
            console.log('Device reboot failed!', error);
            notify.error(gettext('Device reboot failed!'));
        });
    };

    $scope.deviceStart = function (device) {
        $http.post('/api/lmn/device-manager/start', { device: device }).then(function (resp) {
            notify.success(gettext('Device start successful initiated!'));
            setTimeout(function () {
                $scope.checkStatus();
            }, 3000);
        }, function (error) {
            console.log('Device start failed!', error);
            notify.error(gettext('Device start failed!'));
        });
    };

    $scope.deviceLinboRemote = function (device, prestart) {
        $scope.linboRemoteSelectedDevice = device;
        $scope.linboRemotePrestart = prestart;
        $uibModal.open({
            templateUrl: '/lmn.device-manager:resources/partial/linboremote.modal.html',
            controller: 'LMP_DeviceManagerLinboRemoteController',
            backdrop: 'static',
            size: 'mg',
            scope: $scope // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        });
    };

    $scope.openRunningProcesses = function () {
        $uibModal.open({
            templateUrl: '/lmn.device-manager:resources/partial/runningprocesses.modal.html',
            controller: 'LMP_DeviceManagerRunningProcessesController',
            backdrop: 'static',
            size: 'mg',
            scope: $scope // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        });
    };

    $scope.openPreStartCommands = function () {
        $uibModal.open({
            templateUrl: '/lmn.device-manager:resources/partial/prestartcommands.modal.html',
            controller: 'LMP_DeviceManagerPreStartCommandsController',
            backdrop: 'static',
            size: 'mg',
            scope: $scope // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        });
    };

    $scope.updateAutoRefreshStatusTimer = function () {
        $scope.autoRefreshStatusTimerCurrent = $scope.autoRefreshStatusTimerStart;
    };

    $scope.checkCheckedDevices = function () {
        $scope.deviceListFilteredChecked = [];
        for (var _device in $scope.deviceListFiltered) {
            if ($scope.deviceListFiltered[_device].checked && "hostname" in $scope.deviceListFiltered[_device]) {
                $scope.deviceListFilteredChecked.push($scope.deviceListFiltered[_device]);
            }
        }
        console.log($scope.deviceListFilteredChecked);
    };

    $scope.devicesToggleSelection = function () {
        if ($scope.allDevicesSelected) {
            $scope.allDevicesSelected = false;
        } else {
            $scope.allDevicesSelected = true;
        }
        for (var _device2 in $scope.deviceListFiltered) {
            $scope.deviceListFiltered[_device2].checked = $scope.allDevicesSelected;
        }
        $scope.checkCheckedDevices();
    };

    $scope.deviceActionForAll = function (_action) {
        $uibModal.open({
            templateUrl: '/lmn.device-manager:resources/partial/actionForAllDevices.modal.html',
            controller: 'LMP_DeviceManagerActionForAllDevicesController',
            backdrop: 'static',
            size: 'mg',
            resolve: {
                deviceListFilteredChecked: function deviceListFilteredChecked() {
                    return $scope.deviceListFilteredChecked;
                },
                action: function action() {
                    return _action;
                }
            }
        });
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

angular.module('lmn.device-manager').controller('LMP_DeviceManagerLinboRemoteController', function ($scope, $http, pageTitle, gettext, notify, $uibModalInstance) {
    $http.post('/api/lmn/device-manager/getlinboconfig', { device: $scope.linboRemoteSelectedDevice }).then(function (resp) {
        $scope.linboRemoteSelectedDevice.linboconfig = resp.data;
        var _iteratorNormalCompletion5 = true;
        var _didIteratorError5 = false;
        var _iteratorError5 = undefined;

        try {
            for (var _iterator5 = $scope.linboRemoteSelectedDevice.linboconfig[Symbol.iterator](), _step5; !(_iteratorNormalCompletion5 = (_step5 = _iterator5.next()).done); _iteratorNormalCompletion5 = true) {
                var os = _step5.value;

                $http.post('/api/lmn/device-manager/getlastsync', { device: $scope.linboRemoteSelectedDevice, image: os.BaseImage }).then(function (resp) {
                    $scope.linboRemoteSelectedDevice.lastsync = resp.data;
                });
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
    });

    $scope.updateLinboCommand = function () {
        $scope.linbocommand = "linbo-remote -s " + $scope.linboRemoteSelectedDevice.school + " -i " + $scope.linboRemoteSelectedDevice.hostname;
        var tmp = "";

        if ($scope.linboRemoteSelectedDevice.disablegui) {
            $scope.linbocommand += " -d";
        }

        if ($scope.linboRemoteSelectedDevice.format) {
            tmp += "format,";
        }
        if ($scope.linboRemoteSelectedDevice.partition) {
            tmp += "partition,";
        }
        if ($scope.linboRemoteSelectedDevice.initcache) {
            tmp += "initcache,";
        }

        var _iteratorNormalCompletion6 = true;
        var _didIteratorError6 = false;
        var _iteratorError6 = undefined;

        try {
            for (var _iterator6 = $scope.linboRemoteSelectedDevice.linboconfig[Symbol.iterator](), _step6; !(_iteratorNormalCompletion6 = (_step6 = _iterator6.next()).done); _iteratorNormalCompletion6 = true) {
                var os = _step6.value;

                var osNumber = $scope.linboRemoteSelectedDevice.linboconfig.indexOf(os) + 1;
                if (os.format) {
                    tmp += "format:" + osNumber + ",";
                }
                if (os.sync) {
                    tmp += "sync:" + osNumber + ",";
                }
                if (os.start) {
                    tmp += "start:" + osNumber + ",";
                }
            }
        } catch (err) {
            _didIteratorError6 = true;
            _iteratorError6 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion6 && _iterator6.return) {
                    _iterator6.return();
                }
            } finally {
                if (_didIteratorError6) {
                    throw _iteratorError6;
                }
            }
        }

        if (tmp.length > 0) {
            if ($scope.linboRemotePrestart) {
                $scope.linbocommand += " -p " + tmp.substring(0, tmp.length - 1);
            } else {
                $scope.linbocommand += " -c " + tmp.substring(0, tmp.length - 1);
            }
        } else {
            $scope.linbocommand = "";
        }
    };

    $scope.clearAll = function () {
        var _iteratorNormalCompletion7 = true;
        var _didIteratorError7 = false;
        var _iteratorError7 = undefined;

        try {
            for (var _iterator7 = $scope.linboRemoteSelectedDevice.linboconfig[Symbol.iterator](), _step7; !(_iteratorNormalCompletion7 = (_step7 = _iterator7.next()).done); _iteratorNormalCompletion7 = true) {
                var os = _step7.value;

                os.format = false;
                os.sync = false;
                os.start = false;
            }
        } catch (err) {
            _didIteratorError7 = true;
            _iteratorError7 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion7 && _iterator7.return) {
                    _iterator7.return();
                }
            } finally {
                if (_didIteratorError7) {
                    throw _iteratorError7;
                }
            }
        }

        $scope.linboRemoteSelectedDevice.format = false;
        $scope.linboRemoteSelectedDevice.partition = false;
        $scope.linboRemoteSelectedDevice.initcache = false;
        $scope.linboRemoteSelectedDevice.disablegui = false;
    };

    $scope.toggleImageOption = function (os, action) {
        if (os[action]) {
            os[action] = false;
        } else {
            os[action] = true;
        }
        $scope.updateLinboCommand();
    };

    $scope.toggleGlobalOption = function (device, action) {
        if (device[action]) {
            device[action] = false;
        } else {
            device[action] = true;
        }
        $scope.updateLinboCommand();
    };

    $scope.run = function () {
        $http.post('/api/lmn/device-manager/run', { command: $scope.linbocommand }).then(function (resp) {
            if ($scope.linboRemotePrestart) {
                notify.success(gettext('Command successfully stored!'));
                $scope.linbocommand = "";
                $scope.getPrestartCommands();
                $uibModalInstance.close();
            } else {
                $scope.linbocommand = "";
                $scope.linbocommandresult = "Linbo is running...";
                $scope.getRunningLinboRemoteCommands();
                if (!$scope.reloadLinboRemoteLog) {
                    $scope.reloadLinboRemoteLog = setInterval(function () {
                        $http.post('/api/lmn/device-manager/getlinboremotelog', { device: $scope.linboRemoteSelectedDevice }).then(function (resp) {
                            $scope.linbocommandresult = resp.data;
                        });
                    }, 1000);
                }
            }
        }, function (error) {
            notify.error(gettext('Command failed!'));
        });
    };

    $scope.close = function () {
        clearInterval($scope.reloadLinboRemoteLog);
        $scope.clearAll();
        $uibModalInstance.close();
    };
});

angular.module('lmn.device-manager').controller('LMP_DeviceManagerRunningProcessesController', function ($scope, $http, pageTitle, gettext, notify, $uibModalInstance) {

    $scope.loadLog = function (hostname) {
        $scope.linboRemoteLogIsLoading = true;
        if (!$scope.reloadLinboRemoteLog) {
            $scope.reloadLinboRemoteLog = setInterval(function () {
                $http.post('/api/lmn/device-manager/getlinboremotelog', { device: { "hostname": hostname } }).then(function (resp) {
                    $scope.linbocommandresult = resp.data;
                    $scope.linboRemoteLogIsLoading = false;
                });
            }, 1000);
        }
    };

    $scope.close = function () {
        clearInterval($scope.reloadLinboRemoteLog);
        $uibModalInstance.close();
    };
});

angular.module('lmn.device-manager').controller('LMP_DeviceManagerPreStartCommandsController', function ($scope, $http, messagebox, pageTitle, gettext, notify, $uibModalInstance) {

    $scope.removePreStartCommand = function (preStartCommand) {
        $http.post('/api/lmn/device-manager/removePrestartCommands', { preStartCommand: preStartCommand }).then(function (resp) {
            if (resp.data.status) {
                notify.success(gettext('Command deleted successfully!'));
            } else {
                notify.error(gettext('Failed to delete: ') + resp.data.message);
            }
            $scope.getPrestartCommands();
        });
    };

    $scope.editPreStartCommand = function (preStartCommand) {
        messagebox.prompt(gettext("Edit Linbo-Pre-Start Command"), preStartCommand.content).then(function (msg) {
            $http.post('/api/lmn/device-manager/editPrestartCommands', { preStartCommand: preStartCommand, newCommand: msg.value }).then(function (resp) {
                if (resp.data.status) {
                    notify.success(gettext('Command edited successfully!'));
                } else {
                    notify.error(gettext('Failed to edit: ') + resp.data.message);
                }
                $scope.getPrestartCommands();
            });
        });
    };

    $scope.close = function () {
        $uibModalInstance.close();
    };
});

angular.module('lmn.device-manager').controller('LMP_DeviceManagerActionForAllDevicesController', function ($scope, $http, pageTitle, gettext, notify, $uibModalInstance, deviceListFilteredChecked, action) {

    $scope.deviceListFilteredChecked = deviceListFilteredChecked;
    $scope.action = action;

    $scope.actionCounter = 0;
    $scope.successCounter = 0;
    $scope.errorCounter = 0;

    $scope.currentItem = "";
    $scope.errorText = "";

    if (action == "start") {
        var _loop3 = function _loop3(_device3) {
            if ("hostname" in $scope.deviceListFilteredChecked[_device3]) {
                $http.post('/api/lmn/device-manager/start', { device: $scope.deviceListFilteredChecked[_device3] }).then(function (resp) {
                    console.log(resp.data);
                    $scope.currentItem = $scope.deviceListFilteredChecked[_device3];
                    if (resp.data.status) {
                        $scope.successCounter = $scope.successCounter + 1;
                    } else {
                        $scope.errorCounter = $scope.errorCounter + 1;
                        $scope.errorText += $scope.deviceListFilteredChecked[_device3].hostname + ": " + resp.data.message + "\n";
                    }
                    $scope.actionCounter = $scope.actionCounter + 1;
                    if ($scope.actionCounter == $scope.deviceListFilteredChecked.length) {
                        $scope.currentItem = "finished";
                    }
                });
            }
        };

        for (var _device3 in $scope.deviceListFilteredChecked) {
            _loop3(_device3);
        }
    }

    if (action == "shutdown") {
        var _loop4 = function _loop4(_device4) {
            if ("hostname" in $scope.deviceListFilteredChecked[_device4]) {
                $http.post('/api/lmn/device-manager/shutdown', { device: $scope.deviceListFilteredChecked[_device4] }).then(function (resp) {
                    console.log(resp.data);
                    $scope.currentItem = $scope.deviceListFilteredChecked[_device4];
                    if (resp.data.status) {
                        $scope.successCounter = $scope.successCounter + 1;
                    } else {
                        $scope.errorCounter = $scope.errorCounter + 1;
                        $scope.errorText += $scope.deviceListFilteredChecked[_device4].hostname + ": " + resp.data.message + "\n";
                    }
                    $scope.actionCounter = $scope.actionCounter + 1;
                    if ($scope.actionCounter == $scope.deviceListFilteredChecked.length) {
                        $scope.currentItem = "finished";
                    }
                });
            }
        };

        for (var _device4 in $scope.deviceListFilteredChecked) {
            _loop4(_device4);
        }
    }

    if (action == "reboot") {
        var _loop5 = function _loop5(_device5) {
            if ("hostname" in $scope.deviceListFilteredChecked[_device5]) {
                $http.post('/api/lmn/device-manager/reboot', { device: $scope.deviceListFilteredChecked[_device5] }).then(function (resp) {
                    console.log(resp.data);
                    $scope.currentItem = $scope.deviceListFilteredChecked[_device5];
                    if (resp.data.status) {
                        $scope.successCounter = $scope.successCounter + 1;
                    } else {
                        $scope.errorCounter = $scope.errorCounter + 1;
                        $scope.errorText += $scope.deviceListFilteredChecked[_device5].hostname + ": " + resp.data.message + "\n";
                    }
                    $scope.actionCounter = $scope.actionCounter + 1;
                    if ($scope.actionCounter == $scope.deviceListFilteredChecked.length) {
                        $scope.currentItem = "finished";
                    }
                });
            }
        };

        for (var _device5 in $scope.deviceListFilteredChecked) {
            _loop5(_device5);
        }
    }

    if (action == "linbo-remote") {
        // TODO
    }

    if (action == "linbo-remote-prestart") {
        // TODO
    }

    $scope.close = function () {
        $uibModalInstance.close();
    };
});


