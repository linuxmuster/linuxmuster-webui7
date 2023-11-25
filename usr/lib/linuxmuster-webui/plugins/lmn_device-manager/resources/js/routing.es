angular.module('lmn.device-manager').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/device-manager', {
        templateUrl: '/lmn.device-manager:resources/partial/index.html',
        controller: 'LMP_DeviceManagerIndexController',
    });
});
