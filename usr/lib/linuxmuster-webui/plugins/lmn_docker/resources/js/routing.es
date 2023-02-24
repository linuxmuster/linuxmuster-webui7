angular.module('lmn.docker').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/docker', {
        templateUrl: '/lmn_docker:resources/partial/index.html',
        controller: 'DockerLMNIndexController',
    });
});
