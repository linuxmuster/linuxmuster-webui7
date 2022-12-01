angular.module('lmn.vdi_dashboard').controller('Lmn_vdi_dashboardIndexController', function ($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Lmn_vdi_dashboard'));

    $http.get('/api/lmn/vdi/administration/clones').then((resp) => {
        if(resp.data.status == "success") {
            $scope.vdiClones = resp.data.data;
        }
        else {
            notify.error(resp.data.message);
            $scope.vdiClones = {};
        }
    });

    $scope.startVdiSession = (group) => {
        $http.get('/api/lmn/vdi/dashboard/vdiSession/' + group).then((resp) => {
            console.log(resp.data);
            $scope.filename = resp.data;
            location.href = "/api/lmn/vdi/dashboard/download/" + $scope.filename
        });
    };
    
});

