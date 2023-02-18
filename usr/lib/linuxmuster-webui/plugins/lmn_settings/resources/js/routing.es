angular.module('lmn.settings').config($routeProvider =>
        $routeProvider.when('/view/lmn/globalsettings', {
                   templateUrl: '/lmn_settings:resources/partial/globalSettings.html',
                   controller: 'LMglobalSettingsController'
                })
);

