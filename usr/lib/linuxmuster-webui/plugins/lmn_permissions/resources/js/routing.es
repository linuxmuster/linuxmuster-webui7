angular.module('lmn.permissions').config($routeProvider => {
    $routeProvider.when('/view/permissions', {
        templateUrl: '/lmn_permissions:resources/partial/index.html',
        controller: 'PermissionListIndexController'
    })
});
