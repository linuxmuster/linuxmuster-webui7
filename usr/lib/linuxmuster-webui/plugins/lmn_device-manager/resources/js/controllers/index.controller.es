angular.module('lmn.device-manager').controller('LMP_DeviceManagerIndexController', function($scope, $http, pageTitle, gettext, notify, $uibModal) {
    pageTitle.set(gettext('Device Manager'));

    $scope.start = () => {
        $scope.allDevicesSelected = false;
        $scope.deviceListFilteredChecked = [];
        $scope.runningLinboRemoteCommands = [];
        $scope.preStartCommands = [];

        $http.get('/api/lmn/activeschool').then( (resp) => {
            $scope.identity.profile.activeSchool = resp.data;
            let school = $scope.identity.profile.activeSchool;
    
            if (school == "default-school") {
                $scope.path = '/etc/linuxmuster/sophomorix/default-school/devices.csv';
            }
            else {
                $scope.path = '/etc/linuxmuster/sophomorix/' + school + '/' + school + '.devices.csv';
            }

            $http.post('/api/lmn/device-manager/getdevices', { filepath: $scope.path, school: school }).then( (resp) => {
                $scope.deviceList = resp.data;
                $scope.deviceListFiltered = [];
                $scope.createRoomList();
                $scope.checkStatus();
            });

        });
        $scope.autoRefreshStatus = false;
        $scope.autoRefreshStatusTimerStart = 30;
        $scope.autoRefreshStatusTimerCurrent = $scope.autoRefreshStatusTimerStart;
        setInterval(function() {
            if ($scope.autoRefreshStatus && $scope.deviceListFiltered.length > 0) {
                if ($scope.autoRefreshStatusTimerCurrent == 0) {
                    $scope.checkStatus();
                    $scope.autoRefreshStatusTimerCurrent = $scope.autoRefreshStatusTimerStart;
                }
                else {
                    $scope.autoRefreshStatusTimerCurrent = $scope.autoRefreshStatusTimerCurrent - 1;
                }
            }
        }, 1000);
    }

    $scope.getRunningLinboRemoteCommands = () => {
        $http.get('/api/lmn/device-manager/getrunninglinboremotecommands').then( (resp) => {
            console.log(resp.data);
            $scope.runningLinboRemoteCommands = resp.data;
        });
    }

    $scope.getPrestartCommands = () => {
        $http.get('/api/lmn/device-manager/getPrestartCommands').then( (resp) => {
            $scope.preStartCommands = resp.data;
        });
    }

    $scope.createRoomList = () => {
        $scope.roomList = {};
        for (let device of $scope.deviceList) {
            if (!(device.room in $scope.roomList)) {
                $scope.roomList[device.room] = { "name": device.room, "checked": false };
            }
        }
    }

    $scope.getSelectedRooms = () => {
        $scope.selectedRooms = [];
        for (let room in $scope.roomList) {
            if ($scope.roomList[room].checked) {
                $scope.selectedRooms.push($scope.roomList[room].name)
            }
        }
    }

    $scope.refreshDeviceListFiltered = () => {
        $scope.getSelectedRooms();
        $scope.deviceListFiltered = [];
        for (let device in $scope.deviceList) {
            for (let room of $scope.selectedRooms) {
                if (room == $scope.deviceList[device].room) {
                    $scope.deviceListFiltered.push($scope.deviceList[device]);
                }
            }
        }
        $scope.checkStatus();
    }

    $scope.checkStatus = () => {
        $scope.checkOnline();
        $scope.checkOS();
        $scope.getRunningLinboRemoteCommands();
        $scope.getPrestartCommands();
    }

    $scope.checkOnline = () => {
        for (let device of $scope.deviceListFiltered) {
            $http.post('/api/lmn/device-manager/checkOnline', { device: device }).then( (resp) => {
                device.online = resp.data;
            });
        }
    }

    $scope.checkOS = () => {
        for (let device of $scope.deviceListFiltered) {
            $http.post('/api/lmn/device-manager/checkOS', { device: device }).then( (resp) => {
                device.os = resp.data;
            });
        }
    }

    $scope.deviceShutdown = (device) => {
        $http.post('/api/lmn/device-manager/shutdown', { device: device }).then((resp) => {
            notify.success(gettext('Device shutdown successful initiated!'));
            setTimeout(function () {
                $scope.checkStatus();
            }, 3000);
        }, error => {
            console.log('Device shutdown failed!', error);
            notify.error(gettext('Device shutdown failed!'));
        });
    }

    $scope.deviceReboot = (device) => {
        $http.post('/api/lmn/device-manager/reboot', { device: device }).then((resp) => {
            notify.success(gettext('Device reboot successful initiated!'));
            setTimeout(function () {
                $scope.checkStatus();
            }, 3000);
        }, error => {
            console.log('Device reboot failed!', error);
            notify.error(gettext('Device reboot failed!'));
        });
    }

    $scope.deviceStart = (device) => {
        $http.post('/api/lmn/device-manager/start', { device: device }).then((resp) => {
            notify.success(gettext('Device start successful initiated!'));
            setTimeout(function () {
                $scope.checkStatus();
            }, 3000);
        }, error => {
            console.log('Device start failed!', error);
            notify.error(gettext('Device start failed!'));
        });
    }

    $scope.deviceLinboRemote = (device, prestart) => {
        $scope.linboRemoteSelectedDevice = device;
        $scope.linboRemotePrestart = prestart;
        $uibModal.open({
            templateUrl: '/lmn.device-manager:resources/partial/linboremote.modal.html',
            controller: 'LMP_DeviceManagerLinboRemoteController',
            backdrop  : 'static',
            size: 'mg',
            scope: $scope, // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        });
    }

    $scope.openRunningProcesses = () => {
        $uibModal.open({
            templateUrl: '/lmn.device-manager:resources/partial/runningprocesses.modal.html',
            controller: 'LMP_DeviceManagerRunningProcessesController',
            backdrop  : 'static',
            size: 'mg',
            scope: $scope, // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        });
    }

    $scope.openPreStartCommands = () => {
        $uibModal.open({
            templateUrl: '/lmn.device-manager:resources/partial/prestartcommands.modal.html',
            controller: 'LMP_DeviceManagerPreStartCommandsController',
            backdrop  : 'static',
            size: 'mg',
            scope: $scope, // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        });
    }

    $scope.updateAutoRefreshStatusTimer = () => {
        $scope.autoRefreshStatusTimerCurrent = $scope.autoRefreshStatusTimerStart;
    }

    $scope.checkCheckedDevices = () => {
        $scope.deviceListFilteredChecked = [];
        for (let device in $scope.deviceListFiltered) {
            if ($scope.deviceListFiltered[device].checked && "hostname" in $scope.deviceListFiltered[device]) {
                $scope.deviceListFilteredChecked.push($scope.deviceListFiltered[device]);
            }
        }
        console.log($scope.deviceListFilteredChecked);
    }

    $scope.devicesToggleSelection = () => {
        if ($scope.allDevicesSelected) {
            $scope.allDevicesSelected = false;
        }
        else {
            $scope.allDevicesSelected = true;
        }
        for (let device in $scope.deviceListFiltered) {
            $scope.deviceListFiltered[device].checked = $scope.allDevicesSelected;
        }
        $scope.checkCheckedDevices();
    }

    $scope.deviceActionForAll = (action) => {
        $uibModal.open({
            templateUrl : '/lmn.device-manager:resources/partial/actionForAllDevices.modal.html',
            controller  : 'LMP_DeviceManagerActionForAllDevicesController',
            backdrop: 'static',
            size: 'mg',
            resolve: { 
                deviceListFilteredChecked: function() { return $scope.deviceListFilteredChecked; },
                action: function() { return action; }
            }
        })
    }

    $scope.$watch('identity.user', function() {
        if ($scope.identity.user == undefined) { return; }
        if ($scope.identity.user == null) { return; }

        $scope.user = $scope.identity.profile;
        $scope.start();
    });
});

angular.module('lmn.device-manager').controller('LMP_DeviceManagerLinboRemoteController', function($scope, $http, pageTitle, gettext, notify, $uibModalInstance) {
    $http.post('/api/lmn/device-manager/getlinboconfig', { device: $scope.linboRemoteSelectedDevice }).then( (resp) => {
        $scope.linboRemoteSelectedDevice.linboconfig = resp.data;
        for (let os of $scope.linboRemoteSelectedDevice.linboconfig) {
            $http.post('/api/lmn/device-manager/getlastsync', { device: $scope.linboRemoteSelectedDevice, image: os.BaseImage }).then( (resp) => {
                $scope.linboRemoteSelectedDevice.lastsync = resp.data;
            });
        }
    });

    $scope.updateLinboCommand = () => {
        $scope.linbocommand = "linbo-remote -s " + $scope.linboRemoteSelectedDevice.school + " -i " + $scope.linboRemoteSelectedDevice.hostname;
        let tmp = "";

        if ($scope.linboRemoteSelectedDevice.disablegui) {
            $scope.linbocommand  += " -d";
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

        for (let os of $scope.linboRemoteSelectedDevice.linboconfig) {
            let osNumber = $scope.linboRemoteSelectedDevice.linboconfig.indexOf(os) + 1;
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

        if (tmp.length > 0) {
            if ($scope.linboRemotePrestart) {
                $scope.linbocommand += " -p " + tmp.substring(0, tmp.length - 1);
            }
            else {
                $scope.linbocommand += " -c " + tmp.substring(0, tmp.length - 1);
            }
        }
        else {
            $scope.linbocommand = "";
        }
    }

    $scope.clearAll = () => {
        for (let os of $scope.linboRemoteSelectedDevice.linboconfig) {
            os.format = false;
            os.sync = false;
            os.start = false;
        }

        $scope.linboRemoteSelectedDevice.format = false;
        $scope.linboRemoteSelectedDevice.partition = false;
        $scope.linboRemoteSelectedDevice.initcache = false;
        $scope.linboRemoteSelectedDevice.disablegui = false;
    }

    $scope.toggleImageOption = (os, action) => {
        if (os[action]) {
            os[action] = false;
        }
        else {
            os[action] = true;
        }
        $scope.updateLinboCommand();
    }

    $scope.toggleGlobalOption = (device, action) => {
        if (device[action]) {
            device[action] = false;
        }
        else {
            device[action] = true;
        }
        $scope.updateLinboCommand();
    }

    $scope.run = () => {
        $http.post('/api/lmn/device-manager/run', { command: $scope.linbocommand }).then((resp) => {
            if ($scope.linboRemotePrestart) {
                notify.success(gettext('Command successfully stored!'));
                $scope.linbocommand = "";
                $scope.getPrestartCommands();
                $uibModalInstance.close();
            }
            else {
                $scope.linbocommand = "";
                $scope.linbocommandresult = "Linbo is running...";
                $scope.getRunningLinboRemoteCommands();
                if (!$scope.reloadLinboRemoteLog) {
                    $scope.reloadLinboRemoteLog = setInterval(function() {
                        $http.post('/api/lmn/device-manager/getlinboremotelog', { device: $scope.linboRemoteSelectedDevice }).then((resp) => {
                            $scope.linbocommandresult = resp.data;
                        });
                    }, 1000);
                }
            }
        }, error => {
            notify.error(gettext('Command failed!'));
        });
    }

    $scope.close = () => {
        clearInterval($scope.reloadLinboRemoteLog);
        $scope.clearAll();
        $uibModalInstance.close();
    }
});

angular.module('lmn.device-manager').controller('LMP_DeviceManagerRunningProcessesController', function($scope, $http, pageTitle, gettext, notify, $uibModalInstance) {

    $scope.loadLog = (hostname) => {
        $scope.linboRemoteLogIsLoading = true;
        if (!$scope.reloadLinboRemoteLog) {
            $scope.reloadLinboRemoteLog = setInterval(function() {
                $http.post('/api/lmn/device-manager/getlinboremotelog', { device: {"hostname": hostname} }).then((resp) => {
                    $scope.linbocommandresult = resp.data;
                    $scope.linboRemoteLogIsLoading = false;
                });
            }, 1000);
        }
    }
    
    $scope.close = () => {
        clearInterval($scope.reloadLinboRemoteLog);
        $uibModalInstance.close();
    }

});

angular.module('lmn.device-manager').controller('LMP_DeviceManagerPreStartCommandsController', function($scope, $http, messagebox, pageTitle, gettext, notify, $uibModalInstance) {

    $scope.removePreStartCommand = (preStartCommand) => {
        $http.post('/api/lmn/device-manager/removePrestartCommands', { preStartCommand: preStartCommand }).then( (resp) => {
            if (resp.data.status) {
                notify.success(gettext('Command deleted successfully!'));
            }
            else {
                notify.error(gettext('Failed to delete: ') + resp.data.message);
            }
            $scope.getPrestartCommands();
        });
    }

    $scope.editPreStartCommand = (preStartCommand) => {
        messagebox.prompt(gettext("Edit Linbo-Pre-Start Command"), preStartCommand.content).then((msg) => {
            $http.post('/api/lmn/device-manager/editPrestartCommands', { preStartCommand: preStartCommand, newCommand: msg.value }).then( (resp) => {
                if (resp.data.status) {
                    notify.success(gettext('Command edited successfully!'));
                }
                else {
                    notify.error(gettext('Failed to edit: ') + resp.data.message);
                }
                $scope.getPrestartCommands();
            });
        });

    }
    
    $scope.close = () => {
        $uibModalInstance.close();
    }

});

angular.module('lmn.device-manager').controller('LMP_DeviceManagerActionForAllDevicesController', function($scope, $http, pageTitle, gettext, notify, $uibModalInstance, deviceListFilteredChecked, action) {
    
    $scope.deviceListFilteredChecked = deviceListFilteredChecked;
    $scope.action = action;

    $scope.actionCounter = 0;
    $scope.successCounter = 0;
    $scope.errorCounter = 0;

    $scope.currentItem = "";
    $scope.errorText = "";

    if(action == "start") {
        for (let device in $scope.deviceListFilteredChecked) {
            if ("hostname" in $scope.deviceListFilteredChecked[device]) {
                $http.post('/api/lmn/device-manager/start', { device: $scope.deviceListFilteredChecked[device] }).then((resp) => {
                    console.log(resp.data);
                    $scope.currentItem = $scope.deviceListFilteredChecked[device];
                    if(resp.data.status) {
                        $scope.successCounter = $scope.successCounter + 1;
                    }
                    else {
                        $scope.errorCounter = $scope.errorCounter + 1;
                        $scope.errorText += $scope.deviceListFilteredChecked[device].hostname + ": " + resp.data.message + "\n";
                    }
                    $scope.actionCounter = $scope.actionCounter + 1;
                    if ($scope.actionCounter == $scope.deviceListFilteredChecked.length) {
                        $scope.currentItem = "finished";
                    }
                });
            }
        }
    }

    if(action == "shutdown") {
        for (let device in $scope.deviceListFilteredChecked) {
            if ("hostname" in $scope.deviceListFilteredChecked[device]) {
                $http.post('/api/lmn/device-manager/shutdown', { device: $scope.deviceListFilteredChecked[device] }).then((resp) => {
                    console.log(resp.data);
                    $scope.currentItem = $scope.deviceListFilteredChecked[device];
                    if(resp.data.status) {
                        $scope.successCounter = $scope.successCounter + 1;
                    }
                    else {
                        $scope.errorCounter = $scope.errorCounter + 1;
                        $scope.errorText += $scope.deviceListFilteredChecked[device].hostname + ": " + resp.data.message + "\n";
                    }
                    $scope.actionCounter = $scope.actionCounter + 1;
                    if ($scope.actionCounter == $scope.deviceListFilteredChecked.length) {
                        $scope.currentItem = "finished";
                    }
                });
                
            }
        }
    }

    if(action == "reboot") {
        for (let device in $scope.deviceListFilteredChecked) {
            if ("hostname" in $scope.deviceListFilteredChecked[device]) {
                $http.post('/api/lmn/device-manager/reboot', { device: $scope.deviceListFilteredChecked[device] }).then((resp) => {
                    console.log(resp.data);
                    $scope.currentItem = $scope.deviceListFilteredChecked[device];
                    if(resp.data.status) {
                        $scope.successCounter = $scope.successCounter + 1;
                    }
                    else {
                        $scope.errorCounter = $scope.errorCounter + 1;
                        $scope.errorText += $scope.deviceListFilteredChecked[device].hostname + ": " + resp.data.message + "\n";
                    }
                    $scope.actionCounter = $scope.actionCounter + 1;
                    if ($scope.actionCounter == $scope.deviceListFilteredChecked.length) {
                        $scope.currentItem = "finished";
                    }
                });
            }
        }
    }

    if(action == "linbo-remote") {
        // TODO
    }

    if(action == "linbo-remote-prestart") {
        // TODO
    }
    
    $scope.close = () => {
        $uibModalInstance.close();
    }

});