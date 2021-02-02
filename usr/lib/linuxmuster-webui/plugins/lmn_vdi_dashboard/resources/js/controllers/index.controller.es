angular.module('lmn_vdi_dashboard').controller('Lmn_vdi_dashboardIndexController', function ($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Lmn_vdi_dashboard'));

    $http.post('/api/lmn_vdi_administration', { action: 'get-clones' }).then((resp) => {
        if(resp.data.status == "success") {
            $scope.vdiClones = resp.data.data;
        }
        else {
            notify.error(resp.data.message);
            $scope.vdiClones = {};
        }
    });

    $scope.startVdiSession = () => {
        $http.post('/api/lmn_vdi_dashboard', { action: 'get-session', username: $scope.identity.user }).then((resp) => {
            $scope.returnValue = resp.data;
            console.log($scope.returnValue);
        });

    };
});

