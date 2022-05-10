angular.module('lmn.samba_shares').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/home', {
        templateUrl: '/lmn_samba_shares:resources/partial/index.html',
        controller: 'HomeIndexController',
    });
});
