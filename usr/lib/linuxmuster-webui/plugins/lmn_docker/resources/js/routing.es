angular.module('lmn.docker').config(($routeProvider) => {
    $routeProvider.when('/view/docker', {
        templateUrl: '/lmn_docker:resources/partial/index.html',
        controller: 'DockerIndexController',
    });
});
