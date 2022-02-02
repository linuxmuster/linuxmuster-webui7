angular.module('lmn.crontab').config(($routeProvider) => {
    $routeProvider.when('/view/lm/crontab', {
        templateUrl: '/lmn_crontab:resources/partial/index.html',
        controller: 'CrontabIndexController',
    });
});
