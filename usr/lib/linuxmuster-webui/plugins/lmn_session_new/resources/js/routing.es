angular.module('lmn.session_new').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/sessionsList', {
        templateUrl: '/lmn_session_new:resources/partial/sessionsList.html',
        controller: 'LMNSessionsListController',
    });

    $routeProvider.when('/view/lmn/session', {
        templateUrl: '/lmn_session_new:resources/partial/session.html',
        controller: 'LMNSessionController',
    });
});
