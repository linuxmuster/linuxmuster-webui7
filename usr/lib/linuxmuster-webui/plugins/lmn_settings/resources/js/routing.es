angular.module('lmn.settings').config($routeProvider =>
        $routeProvider.when('/view/lm/globalsettings', {
                   templateUrl: '/lmn_settings:resources/partial/globalSettings.html',
                   controller: 'LMglobalSettingsController'
                })
);

