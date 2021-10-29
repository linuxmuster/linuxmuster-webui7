angular.module('lmn.unifi').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/unifi', {
        templateUrl: '/lmn_unifi:resources/partial/index.html',
        controller: 'LMN_unifiIndexController',
    });
});
