angular.module('lmn.settings').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/schoolsettings',
        controller: 'LMSettingsController'
        templateUrl: '/lmn_settings:resources/partial/index.html'


angular.module('lmn.settings').controller 'LMSettingsController', ($scope, $location, $http, $uibModal, messagebox, gettext, notify, pageTitle, core, lmFileBackups, validation, customFields) ->
    pageTitle.set(gettext('Settings'))

    $scope.trans = {
        remove: gettext('Remove')
    }

    $scope.activetab = 0
    $scope.custom_fields_role_selector = 'students'

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

    $http.get('/api/lmn/schoolsettings').then (resp) ->
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

    $http.get('/api/lmn/schoolsettings/latex-templates').then (resp) ->
        $scope.templates_individual = resp.data[0]
        $scope.templates_multiple = resp.data[1]

        customFields.load_config().then (resp) ->
            $scope.custom = resp.custom
            $scope.customMulti = resp.customMulti
            $scope.customDisplay = resp.customDisplay
            $scope.proxyAddresses = resp.proxyAddresses

            $scope.templates = {'multiple': '', 'individual': ''}
            $scope.passwordTemplates = resp.passwordTemplates

            for template in $scope.templates_individual
                if template.path == $scope.passwordTemplates.individual
                    $scope.templates.individual = template
                    break

            for template in $scope.templates_multiple
                if template.path == $scope.passwordTemplates.multiple
                    $scope.templates.multiple = template
                    break


    $http.get('/api/lmn/holidays').then (resp) ->
        $scope.holidays = resp.data

    $scope.filterscriptNotEmpty = () ->
        # A filterscript option should not be empty but "---"
        for role in ['students', 'teachers', 'extrastudents']
            if $scope.settings['userfile.' + role + '.csv']['FILTERSCRIPT'] == ""
               $scope.settings['userfile.' + role + '.csv']['FILTERSCRIPT'] = "---"

    $scope.customDisplayOptions = customFields.customDisplayOptions

    # $http.get('/api/lmn/schoolsettings/school-share').then (resp) ->
    #     $scope.schoolShareEnabled = resp.data

    # $scope.setSchoolShare = (enabled) ->
    #     $scope.schoolShareEnabled = enabled
    #     $http.post('/api/lmn/schoolsettings/school-share', enabled)

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
        $http.post('/api/lmn/schoolsettings', $scope.settings).then () ->
            notify.success gettext('Saved')

    $scope.saveAndCheck = () ->
        validPrintserver = validation.isValidDomain($scope.settings.school.PRINTSERVER)
        if validPrintserver != true
            notify.error(validPrintserver)
            return
        $http.post('/api/lmn/schoolsettings', $scope.settings).then () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/check.modal.html'
                controller: 'LMUsersCheckModalController'
                backdrop: 'static'
            )

            notify.success gettext('Saved')

    $scope.saveApplyQuota = () ->
        $http.post('/api/lmn/schoolsettings', $scope.settings).then () ->
            notify.success gettext('Saved')
        $uibModal.open(
            templateUrl: '/lmn_quotas:resources/partial/apply.modal.html'
            controller: 'LMQuotasApplyModalController'
            backdrop: 'static'
        )

    $scope.saveApplyHolidays = () ->
        if document.getElementsByClassName("has-error").length > 0
            notify.error(gettext("Please first correct the mal formated fields."))
            return
        $http.post('/api/lmn/holidays', $scope.holidays).then () ->
            notify.success gettext('Saved')

    $scope.validateDate = (date) ->
        if validation.isValidDate(date) != true
            return 'has-error'
        return

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
        customFields.save(config).then () ->
            notify.success(gettext('Saved'))
