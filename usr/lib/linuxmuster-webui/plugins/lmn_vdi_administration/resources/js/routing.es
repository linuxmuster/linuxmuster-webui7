angular.module('lmn.vdi_administration').config(($routeProvider) => {
    $routeProvider.when('/view/lmn_vdi_administration', {
        templateUrl: '/lmn_vdi_administration:resources/partial/index.html',
        controller: 'Lmn_vdi_administrationIndexController',
    });
});
