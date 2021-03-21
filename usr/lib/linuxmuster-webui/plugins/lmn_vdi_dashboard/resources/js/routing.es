angular.module('lmn.vdi_dashboard').config(($routeProvider) => {
    $routeProvider.when('/view/lmn_vdi_dashboard', {
        templateUrl: '/lmn_vdi_dashboard:resources/partial/index.html',
        controller: 'Lmn_vdi_dashboardIndexController',
    });
});
