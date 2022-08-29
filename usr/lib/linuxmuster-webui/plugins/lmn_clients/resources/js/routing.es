angular.module('lmn.clients').config(($routeProvider) => {
    $routeProvider.when('/view/lmn_clients', {
        templateUrl: '/lmn_clients:resources/partial/index.html',
        controller: 'Lmn_clientsIndexController',
    });
});
