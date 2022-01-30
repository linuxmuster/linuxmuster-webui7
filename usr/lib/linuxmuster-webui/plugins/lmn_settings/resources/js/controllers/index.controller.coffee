angular.module('lmn.settings').config ($routeProvider) ->
    $routeProvider.when '/view/lm/schoolsettings',
        controller: 'LMSettingsController'
        templateUrl: '/lmn_settings:resources/partial/index.html'


angular.module('lmn.settings').controller 'LMSettingsController', ($scope, $location, $http, $uibModal, messagebox, gettext, notify, pageTitle, core, lmFileBackups, validation) ->
    pageTitle.set(gettext('Settings'))

    $scope.trans = {
        remove: gettext('Remove')
    }

    $scope.tabs = ['general', 'listimport', 'quota', 'printing']

    tag = $location.$$url.split("#")[1]
    if tag and tag in $scope.tabs
        $scope.activetab = $scope.tabs.indexOf(tag)
    else
        $scope.activetab = 0

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
        'UTF8',
    ]

    $scope.customDisplayOptions = ['']
    $scope.customDisplayOptions.push('proxyAddresses')
    for n in [1,2,3,4,5]
        $scope.customDisplayOptions.push('sophomorixCustom' + n)
    for n in [1,2,3,4,5]
        $scope.customDisplayOptions.push('sophomorixCustomMulti' + n)

    $http.get('/api/lm/schoolsettings').then (resp) ->
        school = 'default-school'
        encoding = {}
        #TODO: Remove comments
        #for file in ['userfile.students.csv', 'userfile.teachers.csv', 'userfile.extrastudents.csv', 'classfile.extraclasses.csv', ]
        for file in ['userfile.students.csv', 'userfile.extrastudents.csv', 'userfile.teachers.csv',  'userfile.extrastudents.csv']
            userfile = file.substring(file.indexOf('.')+1)
            if resp.data[file]['ENCODING'] is 'auto'
                console.log('is auto')
                $http.post('/api/lmn/schoolsettings/determine-encoding', {path: '/etc/linuxmuster/sophomorix/'+school+'/'+userfile, file:file}).then (response) ->
                    encoding[response['config']['data']['file']] = response.data
                    console.log(encoding)
        #console.log(encoding)
        $scope.encoding = encoding
        $scope.settings = resp.data

    $http.get('/api/lm/schoolsettings/latex-templates').then (resp) ->
        $scope.templates_individual = resp.data[0]
        $scope.templates_multiple = resp.data[1]

    $http.get('/api/lm/subnets').then (resp) ->
        $scope.subnets = resp.data

    $http.get('/api/lm/holidays').then (resp) ->
        $scope.holidays = resp.data

    $scope.filterscriptNotEmpty = () ->
        # A filterscript option should not be empty but "---"
        for role in ['students', 'teachers', 'extrastudents']
            if $scope.settings['userfile.' + role + '.csv']['FILTERSCRIPT'] == ""
               $scope.settings['userfile.' + role + '.csv']['FILTERSCRIPT'] = "---"

    $scope.load_custom_config = () ->
        $http.get('/api/lm/read_custom_config').then (resp) ->
            $scope.custom = resp.data.custom
            $scope.customMulti = resp.data.customMulti
            $scope.customDisplay = resp.data.customDisplay
            $scope.proxyAddresses = resp.data.proxyAddresses

            $scope.templates = {'multiple': '', 'individual': ''}
            $scope.passwordTemplates = resp.data.passwordTemplates

            for template in $scope.templates_individual
                if template.path == $scope.passwordTemplates.individual
                    $scope.templates.individual = template
                    break

            for template in $scope.templates_multiple
                if template.path == $scope.passwordTemplates.multiple
                    $scope.templates.multiple = template
                    break

    # $http.get('/api/lm/schoolsettings/school-share').then (resp) ->
    #     $scope.schoolShareEnabled = resp.data

    # $scope.setSchoolShare = (enabled) ->
    #     $scope.schoolShareEnabled = enabled
    #     $http.post('/api/lm/schoolsettings/school-share', enabled)

    $scope.removeSubnet = (subnet) ->
        messagebox.show({
            text: gettext('Are you sure you want to delete permanently this subnet ?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then () ->
            $scope.subnets.remove(subnet)

    $scope.addSubnet = () ->
        $scope.subnets.push({'routerIp':'', 'network':'', 'beginRange':'', 'endRange':'', 'setupFlag':''})

    $scope.addHoliday = () ->
        $scope.holidays.push({'name':'', 'start':'', 'end':''})

    $scope.removeHoliday = (holiday) ->
        messagebox.show({
            text: gettext('Are you sure you want to delete permanently these holidays ?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then () ->
            $scope.holidays.remove(holiday)

    $scope.save = () ->
        validPrintserver = validation.isValidDomain($scope.settings.school.PRINTSERVER)
        if validPrintserver != true
            notify.error(validPrintserver)
            return
        $http.post('/api/lm/schoolsettings', $scope.settings).then () ->
            notify.success gettext('Saved')

    $scope.saveAndCheck = () ->
        validPrintserver = validation.isValidDomain($scope.settings.school.PRINTSERVER)
        if validPrintserver != true
            notify.error(validPrintserver)
            return
        $http.post('/api/lm/schoolsettings', $scope.settings).then () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/check.modal.html'
                controller: 'LMUsersCheckModalController'
                backdrop: 'static'
            )

            notify.success gettext('Saved')

    $scope.saveApplyQuota = () ->
        $http.post('/api/lm/schoolsettings', $scope.settings).then () ->
            notify.success gettext('Saved')
        $uibModal.open(
            templateUrl: '/lmn_quotas:resources/partial/apply.modal.html'
            controller: 'LMQuotasApplyModalController'
            backdrop: 'static'
        )

    $scope.saveApplySubnets = () ->
        $http.post('/api/lm/subnets', $scope.subnets).then () ->
            notify.success gettext('Saved')

    $scope.saveApplyHolidays = () ->
        $http.post('/api/lm/holidays', $scope.holidays).then () ->
            notify.success gettext('Saved')

    $scope.backups = () ->
        school = "default-school"
        lmFileBackups.show('/etc/linuxmuster/sophomorix/' + school + '/school.conf')

    $scope.saveCustom = () ->
        config = {
            'custom': $scope.custom,
            'customMulti': $scope.customMulti,
            'customDisplay': $scope.customDisplay,
            'proxyAddresses': $scope.proxyAddresses,
            'passwordTemplates': {
                'multiple': $scope.templates.multiple.path,
                'individual': $scope.templates.individual.path,
            },
        }
        $http.post('/api/lm/save_custom_config', {config: config}).then () ->
            notify.success(gettext('Saved'))
            messagebox.show({
                text: gettext("In order for changes to take effect, it's  necessary to restart the Webui. Restart now ?"),
                positive: gettext('Restart'),
                negative: gettext('Later')
            }).then () ->
                core.forceRestart()

