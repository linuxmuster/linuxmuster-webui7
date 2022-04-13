angular.module('lmn.home').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/home', {
        templateUrl: '/lmn_home:resources/partial/index.html',
        controller: 'HomeIndexController',
    });
});
