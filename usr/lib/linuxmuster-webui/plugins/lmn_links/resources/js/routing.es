angular.module('lmn.links').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/links', {
        templateUrl: '/lmn_links:resources/partial/index.html',
        controller: 'LMN_linksIndexController',
    });
});
