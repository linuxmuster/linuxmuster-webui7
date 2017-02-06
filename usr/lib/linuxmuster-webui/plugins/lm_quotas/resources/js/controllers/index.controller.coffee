angular.module('lm.quotas').config ($routeProvider) ->
    $routeProvider.when '/view/lm/quotas',
        controller: 'LMQuotasController'
        templateUrl: '/lm_quotas:resources/partial/index.html'
    $routeProvider.when '/view/lm/quotas-disabled',
        templateUrl: '/lm_quotas:resources/partial/disabled.html'


angular.module('lm.quotas').controller 'LMQuotasApplyModalController', ($scope, $http, $uibModalInstance, gettext, notify) ->
    $scope.logVisible = false
    $scope.isWorking = true
    $scope.showLog = () ->
        $scope.logVisible = true

    $http.get('/api/lm/quotas/apply').then () ->
        $scope.isWorking = false
        notify.success gettext('Update complete')
    .catch (resp) ->
        notify.error gettext('Update failed'), resp.data.message
        $scope.isWorking = false
        $scope.showLog()

    $scope.close = () ->
        $uibModalInstance.close()


angular.module('lm.quotas').controller 'LMQuotasController', ($scope, $http, $uibModal, $location, $q, gettext, lmEncodingMap, notify, pageTitle, lmFileBackups) ->
    pageTitle.set(gettext('Quotas'))

    $scope._ =
        addNewSpecial: null

    $http.get('/api/lm/settings').then (resp) ->
        $scope.teachersEncoding = lmEncodingMap[resp.data.encoding_teachers] or 'ISO8859-1'
        $http.get("/api/lm/users/teachers?encoding=#{$scope.teachersEncoding}").then (resp) ->
            $scope.teachers = resp.data
            for teacher in $scope.teachers
                q = teacher.quota.split('+')
                teacher.quota =
                    home: parseInt(q[0])
                    var: parseInt(q[1])
                teacher.mailquota = parseInt(teacher.mailquota)

    $http.get('/api/lm/settings').then (resp) ->
        if not resp.data.use_quota
            $location.path('/view/lm/quotas-disabled')

    $http.get('/api/lm/quotas').then (resp) ->
        $scope.quotas = resp.data
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
        return $http.get("/api/lm/ldap-search?q=#{q}").then (resp) ->
            return resp.data

    $scope.isSpecialQuota = (login) ->
        return login in (x.login for x in $scope.specialQuotas)

    $scope.isDefaultQuota = (login) ->
        return login in (x.login for x in $scope.defaultQuotas)

    $scope.studentNameCache = {}

    $scope.getStudentName = (login) ->
        if not angular.isDefined($scope.studentNameCache[login])
            $scope.studentNameCache[login] = '...'
            $http.get("/api/lm/ldap-search?q=#{login}").then (resp) ->
                if resp.data.length > 0
                    $scope.studentNameCache[login] = resp.data[0][1].cn[0]
                else
                    $scope.studentNameCache[login] = login
        return $scope.studentNameCache[login]

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
        qs.push $http.post("/api/lm/users/teachers?encoding=#{$scope.teachersEncoding}", teachers)
        qs.push $http.post('/api/lm/quotas', $scope.quotas)

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
                templateUrl: '/lm_quotas:resources/partial/apply.modal.html'
                controller: 'LMQuotasApplyModalController'
                backdrop: 'static'
            )

    $scope.backups = () ->
        lmFileBackups.show('/etc/sophomorix/user/quota.txt')
