angular.module('lmn.crontab').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/crontab', {
        templateUrl: '/lmn_crontab:resources/partial/index.html',
        controller: 'CrontabIndexController',
    });
});
