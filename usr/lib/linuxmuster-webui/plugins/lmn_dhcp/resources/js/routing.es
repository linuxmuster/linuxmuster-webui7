angular.module('lmn.dhcp').config(($routeProvider) => {
    $routeProvider.when('/view/extra_dhcp', {
        templateUrl: '/lmn_dhcp:resources/partial/index.html',
        controller: 'ExtraDhcpIndexController',
    });
});
