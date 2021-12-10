angular.module('lmn.dhcp').config(($routeProvider) => {
    $routeProvider.when('/view/lm/dhcp', {
        templateUrl: '/lmn_dhcp:resources/partial/index.html',
        controller: 'ExtraDhcpIndexController',
    });
});
