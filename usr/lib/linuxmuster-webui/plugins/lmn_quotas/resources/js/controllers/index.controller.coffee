angular.module('lm.quotas').config ($routeProvider) ->
    $routeProvider.when '/view/lm/quotas',
        controller: 'LMQuotasController'
        templateUrl: '/lmn_quotas:resources/partial/index.html'
    $routeProvider.when '/view/lm/quotas-disabled',
        templateUrl: '/lmn_quotas:resources/partial/disabled.html'


angular.module('lm.quotas').controller 'LMQuotasApplyModalController', ($scope, $http, $uibModalInstance, $window, gettext, notify) ->
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
        $window.location.reload()


angular.module('lm.quotas').controller 'LMQuotasController', ($scope, $http, $uibModal, $location, $q, gettext, lmEncodingMap, notify, pageTitle, lmFileBackups) ->
    pageTitle.set(gettext('Quotas'))

    ## TODO
    # Quota for class
    # Quota for project

    $scope.toChange = {
        'teacher': {},
        'student': {},
        'schooladministrator': {}
    }

    $scope._ =
        addNewSpecial: null

    $scope.searchText = gettext('Search user by login, firstname or lastname (min. 3 chars)')

    # Need an array to keep the order ...
    $scope.quota_types = [
        {'type' : 'quota_default_global', 'name' : gettext('Quota default global (MiB)')},
        {'type' : 'quota_default_school', 'name' : gettext('Quota default school (MiB)')},
        {'type' : 'cloudquota_percentage', 'name' : gettext('Cloudquota (%)')},
        {'type' : 'mailquota_default', 'name' : gettext('Mailquota default (MiB)')},
    ]
    $scope.groupquota_types = [
        {
        'type' : 'linuxmuster-global',
        'classname' : gettext('Quota default global (MiB)'),
        'projname' : gettext('Add to default global (MiB)')},
        {
        'type' : 'default-school',
        'classname' : gettext('Quota default school (MiB)'),
        'projname' : gettext('Add to default school (MiB)')},
        {
        'type' : 'mailquota',
        'classname' : gettext('Mailquota default (MiB)'),
        'projname' : gettext('Add to mailquota (MiB)')},
    ]

    $scope.groupquota = 0
    $scope.get_class_quota = () ->
        if !$scope.groupquota
            $http.get('/api/lm/group-quotas').then (resp) ->
                $scope.groupquota = resp.data
                console.log(resp.data.project)

    $http.get('/api/lm/quotas').then (resp) ->
        $scope.non_default = resp.data[0]
        $scope.settings = resp.data[1]

    $scope.$watch '_.addNewSpecial', () ->
        if $scope._.addNewSpecial
            user = $scope._.addNewSpecial

            $scope.non_default[user.role][user.login] = {
                'QUOTA' : angular.copy($scope.settings['role.'+user.role]),
                'displayName' : user.displayName
                }
            $scope._.addNewSpecial = null

    $scope.isDefaultQuota = (role, quota, value) ->
        return $scope.settings[role][quota] != value

    $scope.findUsers = (q, role='') ->
        return $http.post("/api/lm/ldap-search", {role:role, login:q}).then (resp) ->
            return resp.data

    $scope.userToChange = (role, login, quota) ->
        delete $scope.toChange[role][login+"_"+quota]
        ## Default value for a quota in sophomorix
        value = '---'
        if $scope.non_default[role][login]['QUOTA'][quota] != $scope.settings['role.'+role][quota]
            value = $scope.non_default[role][login]['QUOTA'][quota]
        $scope.toChange[role][login+"_"+quota] = {
            'login': login,
            'quota': quota,
            'value': value
        }

    $scope.remove = (role, login) ->
        ## Reset all 3 quotas to default
        $scope.non_default[role][login]['QUOTA'] = angular.copy($scope.settings['role.'+role])
        $scope.userToChange(role, login, 'quota_default_global')
        $scope.userToChange(role, login, 'quota_default_school')
        $scope.userToChange(role, login, 'mailquota_default')
        delete $scope.non_default[role][login]

    $scope.saveApply = () ->
        $http.post('/api/lm/quotas', {toChange : $scope.toChange}).then () ->
            $uibModal.open(
                templateUrl: '/lmn_quotas:resources/partial/apply.modal.html'
                controller: 'LMQuotasApplyModalController'
                backdrop: 'static'
            )

    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/user/quota.txt')
