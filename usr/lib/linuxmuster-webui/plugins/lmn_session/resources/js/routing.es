angular.module('lmn.session').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/sessionsList', {
        templateUrl: '/lmn_session:resources/partial/sessionsList.html',
        controller: 'LMNSessionsListController',
    });

    $routeProvider.when('/view/lmn/session', {
        templateUrl: '/lmn_session:resources/partial/session.html',
        controller: 'LMNSessionController',
    });
});