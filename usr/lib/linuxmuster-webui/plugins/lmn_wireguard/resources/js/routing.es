angular.module('lmn.wireguard').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/wireguard', {
        templateUrl: '/lmn_wireguard:resources/partial/index.html',
        controller: 'Lmn_wireguardIndexController',
    });
});
