angular.module('lmn.nextcloud').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/nextcloud', {
        templateUrl: '/lmn_nextcloud:resources/partial/index.html',
        controller: 'LMN_nextcloudIndexController',
    });
});
