angular.module('lmn.vdi_dashboard').controller('Lmn_vdi_dashboardIndexController', function ($scope, $http, pageTitle, gettext, notify) {
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

    $scope.startVdiSession = (group) => {
        $http.post('/api/lmn_vdi_dashboard', { action: 'get-vdiSession', username: $scope.identity.user, group: group }).then((resp) => {
            console.log(resp.data);
            $scope.filename = resp.data;
            location.href = "/api/lmn_vdi_dashboard/download/" + $scope.filename
        });
    };
    
});

