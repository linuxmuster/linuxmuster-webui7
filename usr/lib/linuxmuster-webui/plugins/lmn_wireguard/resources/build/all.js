'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('lmn.wireguard', ['core']);


'use strict';

angular.module('lmn.wireguard').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/wireguard', {
        templateUrl: '/lmn_wireguard:resources/partial/index.html',
        controller: 'Lmn_wireguardIndexController'
    });
});


'use strict';

angular.module('lmn.wireguard').controller('Lmn_wireguardIndexController', function ($scope, $http, $uibModal, pageTitle, gettext, notify, messagebox) {
    pageTitle.set(gettext('Wireguard'));

    $scope.status = {};

    $scope.loadPeers = function () {
        $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers", "method": "GET" }).then(function (resp) {
            $scope.peers = resp.data;
            $scope.loadStatus();
        });
    };

    $scope.loadStatus = function () {
        $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/status", "method": "GET" }).then(function (resp) {
            $scope.status = resp.data;
            console.log(resp.data);
        });
    };

    $scope.showConfig = function (peer) {
        $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/" + peer + "/config", "method": "GET" }).then(function (resp) {
            $uibModal.open({
                template: "<div style='margin:10px;'><h2>Wireguard-Konfiguration \"" + peer + "\"</h2><pre>" + resp.data.data + "</pre></div>",
                size: 'mg'
            });
        });
    };

    $scope.showQRCode = function (peer) {
        $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/" + peer + "/qr/b64", "method": "GET" }).then(function (resp) {
            $uibModal.open({
                template: "<div style='margin:10px;'><h2>Wireguard-Konfiguration \"" + peer + "\"</h2><img style='width:100%;' src='data:image/png;base64," + resp.data + "'/></div>",
                size: 'mg'
            });
        });
    };

    $scope.create = function () {
        messagebox.prompt(gettext('Name') + ": ").then(function (msg) {
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers", "method": "POST", "data": { "name": msg.value } }).then(function (resp) {
                notify.success(gettext("Created succesfully!"));
                $scope.loadPeers();
                $scope.askRestart();
            });
        });
    };

    $scope.delete = function (peer) {
        messagebox.show({
            text: gettext("Do you really want to delete this peer?"),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(function () {
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/" + peer, "method": "DELETE" }).then(function (resp) {
                notify.success(gettext("Deleted succesfully!"));
                $scope.loadPeers();
                $scope.askRestart();
            });
        });
    };

    $scope.restart = function () {
        messagebox.show({
            text: gettext("Do you really want to restart the wireguard server? All clients have to reconnected!"),
            positive: gettext('Restart'),
            negative: gettext('Cancel')
        }).then(function () {
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/restart", "method": "GET" }).then(function (resp) {
                notify.success(gettext("Restarted succesfully!"));
                $scope.loadPeers();
            });
        });
    };

    $scope.askRestart = function () {
        messagebox.show({
            text: gettext("The configuration has changed. Do you want to restart the server?"),
            positive: gettext('Restart'),
            negative: gettext('Cancel')
        }).then(function () {
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/restart", "method": "GET" }).then(function (resp) {
                notify.success(gettext("Restarted succesfully!"));
                $scope.loadPeers();
            });
        });
    };

    $scope.import = function () {
        $uibModal.open({
            templateUrl: '/lmn_wireguard:resources/partial/import.modal.html',
            controller: 'Lmn_wireguardImportModalController',
            backdrop: 'static',
            size: 'mg',
            scope: $scope // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        }).result.then(function (result) {
            if (result) {
                $scope.askRestart();
            }
            $scope.loadPeers();
        });
    };

    $scope.loadPeers();
});

angular.module('lmn.wireguard').controller('Lmn_wireguardImportModalController', function ($scope, $http, pageTitle, gettext, notify, $uibModalInstance) {

    $scope.users = [];

    $http.get('/api/lmn/sophomorixUsers/students').then(function (resp) {
        $scope.users = $scope.users.concat(resp.data);
    });

    $http.get('/api/lmn/sophomorixUsers/teachers').then(function (resp) {
        $scope.users = $scope.users.concat(resp.data);
    });

    $scope.checkUser = function () {

        $scope.userprefix = "lmn-user_";

        $scope.userstoimport = [];
        $scope.peerstodelete = [];

        var _loop = function _loop(i) {
            var result = false;
            angular.forEach($scope.peers, function (element) {
                if ($scope.userprefix + $scope.users[i].sAMAccountName == element.name) {
                    result = true;
                }
            });
            if (!result) {
                $scope.userstoimport.push($scope.users[i]);
            }
        };

        for (var i = 0; i < $scope.users.length; i++) {
            _loop(i);
        }

        angular.forEach($scope.peers, function (element) {
            var result = false;
            if (!element.name.includes($scope.userprefix)) {
                result = true;
            } else {
                for (var i = 0; i < $scope.users.length; i++) {
                    if (element.name == $scope.userprefix + $scope.users[i].sAMAccountName) {
                        result = true;
                    }
                }
            }
            if (!result) {
                $scope.peerstodelete.push(element);
            }
        });
    };

    $scope.run = function (importonly) {

        $scope.importstatus = 0;
        $scope.importmax = $scope.userstoimport.length;

        for (var i = 0; i < $scope.userstoimport.length; i++) {
            console.log("Create new peer for " + $scope.userprefix + $scope.userstoimport[i].sAMAccountName);
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers", "method": "POST", "data": { "name": $scope.userprefix + $scope.userstoimport[i].sAMAccountName } }).then(function (resp) {
                $scope.importstatus += 1;
                $scope.importprogress = $scope.importstatus / $scope.importmax * 100;
            });
        }

        if (!importonly) {
            $scope.importmax += $scope.peerstodelete.length;
            for (var _i = 0; _i < $scope.peerstodelete.length; _i++) {
                $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/" + $scope.peerstodelete[_i].name, "method": "DELETE" }).then(function (resp) {
                    $scope.importstatus += 1;
                    $scope.importprogress = $scope.importstatus / $scope.importmax * 100;
                });
            }
        }
    };

    $scope.close = function () {
        $uibModalInstance.close(!$scope.importstatus);
    };
});


