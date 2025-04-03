angular.module('lmn.wireguard').controller('Lmn_wireguardIndexController', function($scope, $http, $uibModal, pageTitle, gettext, notify, messagebox) {
    pageTitle.set(gettext('Wireguard'));

    $scope.status = {};

    $scope.loadPeers = () => {
        $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers", "method": "GET" }).then( (resp) => {
            $scope.peers = resp.data;
            $scope.loadStatus();
        });
    }

    $scope.loadStatus = () => {
        $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/status", "method": "GET" }).then( (resp) => {
            $scope.status = resp.data;
            console.log(resp.data);
        }); 
    }

    $scope.showConfig = (peer) => {
        $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/" + peer + "/config", "method": "GET" }).then( (resp) => {
            $uibModal.open({
                template: "<div style='margin:10px;'><h2>Wireguard-Konfiguration \"" + peer + "\"</h2><pre>" + resp.data.data + "</pre></div>",
                size: 'mg'
            });
        });
    }

    $scope.showQRCode = (peer) => {
        $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/" + peer + "/qr/b64", "method": "GET" }).then( (resp) => {
            $uibModal.open({
                template: "<div style='margin:10px;'><h2>Wireguard-Konfiguration \"" + peer + "\"</h2><img style='width:100%;' src='data:image/png;base64," + resp.data + "'/></div>",
                size: 'mg'
            });
        });
    }

    $scope.create = () => {
        messagebox.prompt(gettext('Name') + ": ").then( (msg) => {
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers", "method": "POST", "data": { "name": msg.value } }).then( (resp) => {
                notify.success(gettext("Created succesfully!"))
                $scope.loadPeers();
                $scope.askRestart();
            });
        });
    }

    $scope.delete = (peer) => {
        messagebox.show({
            text: gettext("Do you really want to delete this peer?"),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then( () => {
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/" + peer, "method": "DELETE" }).then( (resp) => {
                notify.success(gettext("Deleted succesfully!"))
                $scope.loadPeers();
                $scope.askRestart();
            });
        });   
    }

    $scope.restart = () => {
        messagebox.show({
            text: gettext("Do you really want to restart the wireguard server? All clients have to reconnected!"),
            positive: gettext('Restart'),
            negative: gettext('Cancel')
        }).then( () => {
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/restart", "method": "GET" }).then( (resp) => {
                notify.success(gettext("Restarted succesfully!"))
                $scope.loadPeers();
            });
        });   
    }

    $scope.askRestart = () => {
        messagebox.show({
            text: gettext("The configuration has changed. Do you want to restart the server?"),
            positive: gettext('Restart'),
            negative: gettext('Cancel')
        }).then( () => {
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/restart", "method": "GET" }).then( (resp) => {
                notify.success(gettext("Restarted succesfully!"))
                $scope.loadPeers();
            });
        });   
    }

    $scope.import = () => {
        $uibModal.open({
            templateUrl: '/lmn_wireguard:resources/partial/import.modal.html',
            controller: 'Lmn_wireguardImportModalController',
            backdrop  : 'static',
            size: 'mg',
            scope: $scope, // https://stackoverflow.com/questions/30709962/reload-list-after-closing-modal
        }).result.then((result) => {
            if(result){
                $scope.askRestart();
            }
            $scope.loadPeers();
        });
    }

    $scope.loadPeers();
});

angular.module('lmn.wireguard').controller('Lmn_wireguardImportModalController', function($scope, $http, pageTitle, gettext, notify, $uibModalInstance) {

    $scope.users = [];

    $http.get('/api/lmn/sophomorixUsers/students').then( (resp) => {
        $scope.users = $scope.users.concat(resp.data);
    });

    $http.get('/api/lmn/sophomorixUsers/teachers').then( (resp) => {
        $scope.users = $scope.users.concat(resp.data);
    });

    $scope.checkUser = () => {

        $scope.userprefix = "lmn-user_";

        $scope.userstoimport = [];
        $scope.peerstodelete = [];

        for (let i = 0; i < $scope.users.length; i++) {
            let result = false;
            angular.forEach($scope.peers, function(element) {
                if (($scope.userprefix + $scope.users[i].sAMAccountName) == element.name) {
                    result = true;
                }
            });
            if(!result) {
                $scope.userstoimport.push($scope.users[i])
            }
        }

        angular.forEach($scope.peers, function(element) {
            let result = false;
            if (!element.name.includes($scope.userprefix)) {
                result = true;
            }
            else {
                for (let i = 0; i < $scope.users.length; i++) {
                    if (element.name == ($scope.userprefix + $scope.users[i].sAMAccountName)) {
                        result = true;
                    }
                }
            }
            if(!result) {
                $scope.peerstodelete.push(element)
            }
        });

    }

    $scope.run = (importonly) => {

        $scope.importstatus = 0;
        $scope.importmax = $scope.userstoimport.length;

        for (let i = 0; i < $scope.userstoimport.length; i++) {
            console.log("Create new peer for " + $scope.userprefix + $scope.userstoimport[i].sAMAccountName)
            $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers", "method": "POST", "data": { "name": $scope.userprefix + $scope.userstoimport[i].sAMAccountName } }).then( (resp) => {
                $scope.importstatus += 1;
                $scope.importprogress = ($scope.importstatus / $scope.importmax) * 100;
            });
        }

        if(!importonly) {
            $scope.importmax += $scope.peerstodelete.length;
            for (let i = 0; i < $scope.peerstodelete.length; i++) {
                $http.post('/api/lmn/wireguard', { "url": "/api/wireguard/peers/" + $scope.peerstodelete[i].name, "method": "DELETE" }).then( (resp) => {
                    $scope.importstatus += 1;
                    $scope.importprogress = ($scope.importstatus / $scope.importmax) * 100;
                });
            }
        }

    }
    
    $scope.close = () => {
        $uibModalInstance.close(!$scope.importstatus);
    }

});