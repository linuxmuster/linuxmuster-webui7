angular.module('lmn.docker').config(($routeProvider) => {
    $routeProvider.when('/view/lm/docker', {
        templateUrl: '/lmn_docker:resources/partial/index.html',
        controller: 'DockerLMNIndexController',
    });
});
