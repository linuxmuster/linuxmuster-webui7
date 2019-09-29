angular.module('lm.quotas').config ($routeProvider) ->
    $routeProvider.when '/view/lm/quotas',
        controller: 'LMQuotasController'
        templateUrl: '/lmn_quotas:resources/partial/index.html'
    $routeProvider.when '/view/lm/quotas-disabled',
        templateUrl: '/lmn_quotas:resources/partial/disabled.html'


angular.module('lm.quotas').controller 'LMQuotasApplyModalController', ($scope, $http, $uibModalInstance, gettext, notify) ->
    $scope.logVisible = true
    $scope.isWorking = true

    $http.get('/api/lm/quotas/apply').then () ->
        $scope.isWorking = false
        notify.success gettext('Update complete')
    .catch (resp) ->
        notify.error gettext('Update failed'), resp.data.message
        $scope.isWorking = false
        $scope.logVisible = true

    $scope.close = () ->
        $uibModalInstance.close()


angular.module('lm.quotas').controller 'LMQuotasController', ($scope, $http, $uibModal, $location, $q, gettext, lmEncodingMap, notify, pageTitle, lmFileBackups) ->
    pageTitle.set(gettext('Quotas'))

    $scope._ =
        addNewSpecial: null

    #$http.get("/api/lm/users/teachers-list").then (resp) ->
        #$scope.teachers = resp.data
        #for teacher in $scope.teachers
            #teacher.quota = parseInt(teacher.quota)
            #teacher.mailquota = parseInt(teacher.mailquota)

    #$http.get('/api/lm/settings').then (resp) ->
        #if not resp.data.use_quota
            #$location.path('/view/lm/quotas-disabled')
            
    $http.get('/api/lm/schoolsettings').then (resp) ->
        school = 'default-school'
        $scope.settings = resp.data

    $http.get('/api/lm/quotas').then (resp) ->
        $scope.quotas = resp.data[0]
        $scope.teachers = resp.data[1]
        $scope.standardQuota = $scope.quotas['standard-lehrer']

    $http.get('/api/lm/class-quotas').then (resp) ->
        $scope.classes = resp.data
        $scope.originalClasses = angular.copy($scope.classes)

    $http.get('/api/lm/project-quotas').then (resp) ->
        $scope.projects = resp.data
        $scope.originalProjects = angular.copy($scope.projects)

    $scope.specialQuotas = [
        {login: 'www-data', name: gettext('Webspace')}
        {login: 'administrator', name: gettext('Main admin')}
        {login: 'pgmadmin', name: gettext('Program admin')}
        {login: 'wwwadmin', name: gettext('Web admin')}
    ]

    $scope.defaultQuotas = [
        {login: 'standard-workstations', name: gettext('Workstation default')}
        {login: 'standard-schueler', name: gettext('Student default')}
        {login: 'standard-lehrer', name: gettext('Teacher default')}
    ]

    $scope.$watch '_.addNewSpecial', () ->
        if $scope._.addNewSpecial
            $scope.quotas[$scope._.addNewSpecial] = angular.copy($scope.standardQuota)
            $scope._.addNewSpecial = null

    $scope.findUsers = (q) ->
        return $http.get("/api/lm/ldap-search?login=#{q}").then (resp) ->
            return resp.data

    $scope.isSpecialQuota = (login) ->
        return login in (x.login for x in $scope.specialQuotas)

    $scope.isDefaultQuota = (login) ->
        return login in (x.login for x in $scope.defaultQuotas)

    $scope.NameCache = {}

    $scope.getName = (login) ->
        if not angular.isDefined($scope.NameCache[login])
            $scope.NameCache[login] = '...'
            $http.get("/api/lm/ldap-search?login=#{login}").then (resp) ->
                if resp.data
                    $scope.NameCache[login] = resp.data.sn + " " + resp.data.givenName
                else
                    $scope.NameCache[login] = login
        return $scope.NameCache[login]

    $scope.remove = (login) ->
        delete $scope.quotas[login]

    $scope.save = () ->
        teachers = angular.copy($scope.teachers)
        for teacher in teachers
            if not teacher.quota.home and not teacher.quota.var
                teacher.quota = ''
            else
                teacher.quota = "#{teacher.quota.home or $scope.standardQuota.home}+#{teacher.quota.var or $scope.standardQuota.var}"
            teacher.mailquota = "#{teacher.mailquota or ''}"

        classesToChange = []
        for cls, index in $scope.classes
            if not angular.equals(cls, $scope.originalClasses[index])
                cls.quota.home ?= $scope.standardQuota.home
                cls.quota.var ?= $scope.standardQuota.var
                classesToChange.push cls

        projectsToChange = []
        for project, index in $scope.projects
            if not angular.equals(project, $scope.originalProjects[index])
                project.quota.home ?= $scope.standardQuota.home
                project.quota.var ?= $scope.standardQuota.var
                projectsToChange.push project

        qs = []
        #qs.push $http.post("/api/lm/users/teachers?encoding=#{$scope.teachersEncoding}", teachers)
        #qs.push $http.post('/api/lm/quotas', $scope.quotas)
        qs.push $http.post('/api/lm/schoolsettings', $scope.settings)

        if classesToChange.length > 0
            qs.push $http.post("/api/lm/class-quotas", classesToChange).then () ->

        if projectsToChange.length > 0
            qs.push $http.post("/api/lm/project-quotas", projectsToChange).then () ->

        return $q.all(qs).then () ->
            $scope.originalClasses = angular.copy($scope.classes)
            $scope.originalProjects = angular.copy($scope.projects)
            notify.success gettext('Saved')

    $scope.saveApply = () ->
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lmn_quotas:resources/partial/apply.modal.html'
                controller: 'LMQuotasApplyModalController'
                backdrop: 'static'
            )

    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/user/quota.txt')
