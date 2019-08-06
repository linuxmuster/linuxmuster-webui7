angular.module('lm.settings').config($routeProvider =>
        $routeProvider.when('/view/lm/webuisettings', {
                   templateUrl: '/lmn_settings:resources/partial/webuiSettings.html',
                   controller: 'LMwebuiSettingsController'
                })
);

