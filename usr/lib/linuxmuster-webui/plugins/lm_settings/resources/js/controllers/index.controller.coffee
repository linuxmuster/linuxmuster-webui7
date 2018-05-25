angular.module('lm.settings').config ($routeProvider) ->
    $routeProvider.when '/view/lm/schoolsettings',
        controller: 'LMSettingsController'
        templateUrl: '/lm_settings:resources/partial/index.html'



angular.module('lm.settings').controller 'LMSettingsController', ($scope, $http, $uibModal, gettext, notify, pageTitle, lmFileBackups) ->
    pageTitle.set(gettext('Settings'))

    $scope.logLevels = [
        {name: gettext('Minimal'), value: 0}
        {name: gettext('Average'), value: 1}
        {name: gettext('Maximal'), value: 2}
    ]

    $scope.encodings = [
        'ascii',
        '8859-1',
        '8859-15',
        'win1252',
        'utf8',
    ]

    $http.get('/api/lm/settings').then (resp) ->
        $scope.settings = resp.data

    $http.get('/api/lm/settings/school-share').then (resp) ->
        $scope.schoolShareEnabled = resp.data

    $scope.setSchoolShare = (enabled) ->
        $scope.schoolShareEnabled = enabled
        $http.post('/api/lm/settings/school-share', enabled)

    $scope.save = () ->
        $http.post('/api/lm/settings', $scope.settings).then () ->
            notify.success gettext('Saved')

    $scope.backups = () ->
        lmFileBackups.show('/etc/sophomorix/user/sophomorix.conf')
