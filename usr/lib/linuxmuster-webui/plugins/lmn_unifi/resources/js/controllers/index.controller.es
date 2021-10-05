angular.module('lmn.unifi').controller('LMN_unifiIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Unifi'));

    $scope.paging = {
        page: 1,
        pageSize: 10
    }
 
    $scope.query = ""

    $scope.refresh = () => {
        $scope.deviceList = [];
        $scope.start();
    }

    $scope.rebootAP = (device) => {
        $http.post('/api/lmn/unifi/rebootDevice', { device: device }).then((resp) => {
            console.log(resp.data);
            if(resp.data.status == "success") {
                notify.success("AP " + device.DEVICE_NAME + " reboot initiated!");
                $scope.start();
            }
            else {
                notify.error("Could not initiate reboot for " + device.DEVICE_NAME + "! - " + resp.data.data);
            }
        });
    };

    $scope.enableAP = (device) => {
        $http.post('/api/lmn/unifi/enableDevice', { device: device }).then((resp) => {
            console.log(resp.data);
            if(resp.data.status == "success") {
                notify.success("AP " + device.DEVICE_NAME + " successful enabled!");
                $scope.start();
            }
            else {
                notify.error("Could not enable " + device.DEVICE_NAME + "!");
            }
        });
    };

    $scope.disableAP = (device) => {
        $http.post('/api/lmn/unifi/disableDevice', { device: device }).then((resp) => {
            console.log(resp.data);
            if(resp.data.status == "success") {
                notify.success("AP " + device.DEVICE_NAME + " successful disabled!");
                $scope.start();
            }
            else {
                notify.error("Could not disable " + device.DEVICE_NAME + "!");
            }
        });
    };

    $scope.toggleAPState = (device) => {
        if(device.DISABLED == "0") {
            $scope.disableAP(device);
        }
        else {
            $scope.enableAP(device);
        }     
    };

    $scope.batchRebootAP = () => {
        if($scope.deviceList) {
            for (var device of $scope.deviceList) {
                if(device.selected) {
                    $scope.rebootAP(device);
                }
            }
        }
    };

    $scope.batchDisableAP = () => {
        if($scope.deviceList) {
            for (var device of $scope.deviceList) {
                if(device.selected) {
                    $scope.disableAP(device);
                }
            }
        }
    };

    $scope.batchEnableAP = () => {
        if($scope.deviceList) {
            for (var device of $scope.deviceList) {
                if(device.selected) {
                    $scope.enableAP(device);
                }
            }
        }
    };

    $scope.start = () => {
        $http.get('/api/lmn/unifi/getDevices').then( (resp) => {
           if(resp.data.status == "success") {
               console.log(resp.data.data);
               $scope.deviceList = resp.data.data;
           }
           else {
               console.log("Error!");
           }
        });
        // setTimeout(function() {
        //     $scope.start();
        // }, 10000);
    };

    $scope.filter = function (item) {
        for (var value of ["DEVICE_NAME", "DEVICE_IP", "DEVICE_MAC"]) {
            if (item[value].toLowerCase().includes($scope.query.toLowerCase())) {
                return true;
            }
        }
        return false;
    };

    $scope.selectAll = function () {
        var newdeviceList = []
        for (var device of $scope.deviceList) {
            if($scope.all_selected) {
                if ($scope.filter(device)) {
                    if(device.selected) {
                        device.selected = false;
                    }
                    else {
                        device.selected = true;
                    }
                }
            }
            else {
                device.selected = false;
            }
            newdeviceList.push(device);
        }
        $scope.deviceList = newdeviceList;
    };

    $scope.haveSelection = function () {
        if($scope.deviceList) {
            for (var device of $scope.deviceList) {
                if(device.selected) {
                    return true;
                }
            }
        }
        return false;
    };

    $scope.$watch('identity.user', function() {
        if ($scope.identity.user == undefined) { return; }
        if ($scope.identity.user == null) { return; }

        $scope.user = $scope.identity.profile;
        $scope.start();
    });
});
