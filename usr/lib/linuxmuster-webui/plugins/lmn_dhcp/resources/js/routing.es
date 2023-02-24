angular.module('lmn.dhcp').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/dhcp', {
        templateUrl: '/lmn_dhcp:resources/partial/index.html',
        controller: 'ExtraDhcpIndexController',
    });
});
