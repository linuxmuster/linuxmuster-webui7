angular.module('lm.settings').config ($routeProvider) ->
    $routeProvider.when '/view/lm/schoolsettings',
        controller: 'LMSettingsController'
        templateUrl: '/lmn_settings:resources/partial/index.html'


angular.module('lm.settings').controller 'LMSettingsController', ($scope, $http, $uibModal, gettext, notify, pageTitle, lmFileBackups) ->
    pageTitle.set(gettext('Settings'))

    $scope.logLevels = [
        {name: gettext('Minimal'), value: 0}
        {name: gettext('Average'), value: 1}
        {name: gettext('Maximal'), value: 2}
    ]

    $scope.unit = 'MiB'

    $scope.encodings = [
        'auto',
        'ASCII',
        'ISO_8859-1',
        'ISO_8859-15',
        'WIN-1252',
        'UTF-8',
    ]

    $http.get('/api/lm/schoolsettings').then (resp) ->
        school = 'default-school'
        console.log(resp.data)
        encoding = {}
        #TODO: Remove comments
        #for file in ['userfile.students.csv', 'userfile.teachers.csv', 'userfile.extrastudents.csv', 'classfile.extraclasses.csv', ]
        for file in ['userfile.students.csv', 'userfile.extrastudents.csv', 'userfile.teachers.csv',  'userfile.extrastudents.csv']
            userfile = file.substring(file.indexOf('.')+1)
            if resp.data[file]['encoding'] is 'auto'
                #console.log(userfile)
                console.log('is auto')
                $http.post('/api/lmn/schoolsettings/determine-encoding', {path: '/etc/linuxmuster/sophomorix/'+school+'/'+userfile, file:file}).then (response) ->
                    encoding[response['config']['data']['file']] = response.data
                    console.log(encoding)
        #console.log(encoding)
        $scope.encoding = encoding
        $scope.settings = resp.data

    # $http.get('/api/lm/schoolsettings/school-share').then (resp) ->
    #     $scope.schoolShareEnabled = resp.data

    # $scope.setSchoolShare = (enabled) ->
    #     $scope.schoolShareEnabled = enabled
    #     $http.post('/api/lm/schoolsettings/school-share', enabled)

    $scope.save = () ->
        $http.post('/api/lm/schoolsettings', $scope.settings).then () ->
            notify.success gettext('Saved')

    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/user/sophomorix.conf')
