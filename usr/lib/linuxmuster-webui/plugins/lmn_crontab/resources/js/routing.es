angular.module('lmn.cron').config(($routeProvider) => {
    $routeProvider.when('/view/cron', {
        templateUrl: '/lmn_cron:resources/partial/index.html',
        controller: 'CronIndexController',
    });
});
