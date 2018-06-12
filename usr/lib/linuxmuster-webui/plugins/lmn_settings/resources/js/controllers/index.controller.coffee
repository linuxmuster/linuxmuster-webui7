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
        'auto',
        'ascii',
        '8859-1',
        '8859-15',
        'win1252',
        'utf8',
    ]

    $http.get('/api/lm/schoolsettings').then (resp) ->
        console.log(resp.data)
        $scope.settings = resp.data

    $http.get('/api/lm/schoolsettings/school-share').then (resp) ->
        $scope.schoolShareEnabled = resp.data

    $scope.setSchoolShare = (enabled) ->
        $scope.schoolShareEnabled = enabled
        $http.post('/api/lm/schoolsettings/school-share', enabled)

    $scope.save = () ->
        $http.post('/api/lm/schoolsettings', $scope.settings).then () ->
            notify.success gettext('Saved')

    $scope.backups = () ->
        lmFileBackups.show('/etc/sophomorix/user/sophomorix.conf')
