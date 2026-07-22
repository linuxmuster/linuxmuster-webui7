angular.module('lmn.settings').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/schoolsettings',
        controller: 'LMSettingsController'
        templateUrl: '/lmn_settings:resources/partial/index.html'


angular.module('lmn.settings').controller 'LMSettingsController', ($scope, $location, $http, $uibModal, messagebox, gettext, notify, pageTitle, core, lmFileBackups, validation, customFields, passwordConstraints) ->
    pageTitle.set(gettext('Settings'))

    $scope.trans = {
        remove: gettext('Remove')
    }

    $scope.activetab = 0
    $scope.custom_fields_role_selector = 'students'
    $scope.isGlobalAdmin = $scope.identity.profile.sophomorixRole == 'globaladministrator'
    $scope.passwordConstraintsRoles = ['student', 'teacher', 'parent', 'staff', 'schooladministrator', 'globaladministrator']
    $scope.passwordConstraintsRole = 'student'
    $scope.passwordRuleClasses = ['lower', 'upper', 'digit', 'special']
    $scope.passwordRuleClassLabels = {
        lower: gettext('Lowercase letter')
        upper: gettext('Uppercase letter')
        digit: gettext('Digit')
        special: gettext('Special character')
    }

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

    buildPasswordRuleForm = (rules) ->
        form = {minLength: null, classes: {lower: false, upper: false, digit: false, special: false}, count: null}
        for rule in rules
            if rule.type == 'min_length'
                form.minLength = rule.value
            else if rule.type == 'require_classes'
                form.classes[cls] = true for cls in rule.classes
                form.count = rule.count
        form

    buildPasswordRulesFromForm = (form) ->
        rules = []
        if form.minLength
            rules.push({type: 'min_length', value: form.minLength})
        selectedClasses = (cls for cls, checked of form.classes when checked)
        if selectedClasses.length > 0
            rule = {type: 'require_classes', classes: selectedClasses}
            rule.count = form.count if form.count
            rules.push(rule)
        rules

    $http.get('/api/lmn/activeschool').then (resp) ->
        $scope.currentSchool = resp.data

        passwordConstraints.load().then (resp) ->
            $scope.passwordConstraints = resp
            $scope.passwordConstraintsForm = {default: {}, schools: {}}

            for role in $scope.passwordConstraintsRoles
                $scope.passwordConstraintsForm.default[role] = buildPasswordRuleForm(resp.default[role] or [])

            for school, roles of resp.schools
                $scope.passwordConstraintsForm.schools[school] = {}
                for role, rules of roles
                    $scope.passwordConstraintsForm.schools[school][role] = buildPasswordRuleForm(rules)

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

    $scope.hasSchoolOverride = (role) ->
        !!($scope.passwordConstraintsForm and $scope.passwordConstraintsForm.schools[$scope.currentSchool] and $scope.passwordConstraintsForm.schools[$scope.currentSchool][role])

    $scope.toggleSchoolOverride = (role) ->
        $scope.passwordConstraintsForm.schools[$scope.currentSchool] ?= {}
        if $scope.hasSchoolOverride(role)
            delete $scope.passwordConstraintsForm.schools[$scope.currentSchool][role]
            if Object.keys($scope.passwordConstraintsForm.schools[$scope.currentSchool]).length == 0
                delete $scope.passwordConstraintsForm.schools[$scope.currentSchool]
        else
            $scope.passwordConstraintsForm.schools[$scope.currentSchool][role] = buildPasswordRuleForm([])

    $scope.savePasswordConstraints = () ->
        config = {schools: {}}

        if $scope.isGlobalAdmin
            config.default = {}
            for role in $scope.passwordConstraintsRoles
                config.default[role] = buildPasswordRulesFromForm($scope.passwordConstraintsForm.default[role])

        for school, roles of $scope.passwordConstraintsForm.schools
            config.schools[school] = {}
            for role, form of roles
                config.schools[school][role] = buildPasswordRulesFromForm(form)

        passwordConstraints.save(config).then () ->
            $scope.passwordConstraints = config
            notify.success gettext('Saved')
