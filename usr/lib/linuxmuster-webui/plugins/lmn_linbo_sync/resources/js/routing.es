angular.module('lmn.linbo_sync').config($routeProvider => {
    $routeProvider.when('/view/lm/synclist', {
        templateUrl: '/lmn_linbo_sync:resources/partial/index.html',
        controller: 'SyncIndexController'
    })
});
