'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('lmn.vdi_dashboard', ['core']);


'use strict';

angular.module('lmn.vdi_dashboard').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn_vdi_dashboard', {
        templateUrl: '/lmn_vdi_dashboard:resources/partial/index.html',
        controller: 'Lmn_vdi_dashboardIndexController'
    });
});


'use strict';

angular.module('lmn.vdi_dashboard').controller('Lmn_vdi_dashboardIndexController', function ($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Lmn_vdi_dashboard'));

    $http.post('/api/lmn_vdi_administration', { action: 'get-clones' }).then(function (resp) {
        if (resp.data.status == "success") {
            $scope.vdiClones = resp.data.data;
        } else {
            notify.error(resp.data.message);
            $scope.vdiClones = {};
        }
    });

    $scope.startVdiSession = function (group) {
        $http.post('/api/lmn_vdi_dashboard', { action: 'get-vdiSession', username: $scope.identity.user, group: group }).then(function (resp) {
            console.log(resp.data);
            $scope.filename = resp.data;
            location.href = "/api/lmn_vdi_dashboard/download/" + $scope.filename;
        });
    };
});


