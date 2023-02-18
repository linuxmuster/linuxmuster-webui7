angular.module('lmn.samba_dns').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/samba_dns', {
        templateUrl: '/lmn_samba_dns:resources/partial/index.html',
        controller: 'SambaDnsIndexController',
    });
});
