angular.module('lmn.quotas').config ($routeProvider) ->
    $routeProvider.when '/view/lm/quotas',
        controller: 'LMQuotasController'
        templateUrl: '/lmn_quotas:resources/partial/index.html'
    $routeProvider.when '/view/lm/quotas-disabled',
        templateUrl: '/lmn_quotas:resources/partial/disabled.html'


angular.module('lmn.quotas').controller 'LMQuotasApplyModalController', ($scope, $http, $uibModalInstance, $window, gettext, notify) ->
    $scope.logVisible = true
    $scope.isWorking = true

    $http.post('/api/lmn/quota/apply').then () ->
        $scope.isWorking = false
        notify.success gettext('Update complete')
    .catch (resp) ->
        notify.error gettext('Update failed'), resp.data.message
        $scope.isWorking = false
        $scope.logVisible = true

    $scope.close = () ->
        $uibModalInstance.close()
        $window.location.reload()


angular.module('lmn.quotas').controller 'LMQuotasController', ($scope, $http, $uibModal, $location, $q, gettext, hotkeys, lmEncodingMap, notify, pageTitle, lmFileBackups, $rootScope, wait) ->
    pageTitle.set(gettext('Quotas'))

    $scope.UserSearchVisible = false
    $scope.activeTab = 0
    $scope.tabs = ['teacher', 'student', 'schooladministrator', 'adminclass', 'project']

    $scope.toChange = {
        'teacher': {},
        'student': {},
        'schooladministrator': {}
    }

    $scope.groupsToChange = {
        'adminclass': {},
        'project': {}
    }

    $scope._ =
        addNewSpecial: null

    $scope.searchText = gettext('Search user by login, firstname or lastname (min. 3 chars), without special char.')

    # Need an array to keep the order ...
    $scope.quota_types = [
        {'type' : 'QUOTA_DEFAULT_GLOBAL', 'name' : gettext('Quota default global (MiB)')},
        {'type' : 'QUOTA_DEFAULT_SCHOOL', 'name' : gettext('Quota default school (MiB)')},
        {'type' : 'CLOUDQUOTA_PERCENTAGE', 'name' : gettext('Cloudquota (%)')},
        {'type' : 'MAILQUOTA_DEFAULT', 'name' : gettext('Mailquota default (MiB)')},
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
            wait.modal(gettext("Retrieving groups quotas ..."), 'progressbar')
            $http.get('/api/lmn/quota/groups').then (resp) ->
                $scope.groupquota = resp.data
                $rootScope.$emit('updateWaiting', 'done')

    $http.get('/api/lmn/quota/quotas').then (resp) ->
        $scope.non_default = resp.data[0]
        $scope.settings = resp.data[1]

    $scope.$watch '_.addNewSpecial', () ->
        if $scope._.addNewSpecial
            user = $scope._.addNewSpecial

            $scope.non_default[user.role][user.login] = {
                'QUOTA' : angular.copy($scope.settings['role.'+user.role]),
                'displayName' : user.displayName
                }
            $scope.non_default[user.role].list.push({'sn':user.sn, 'login':user.login, 'givenname':user.givenName})
            $scope._.addNewSpecial = null
            $scope.UserSearchVisible = false
            notify.success(user.displayName + gettext(" added with default values in the list."))

    $scope.isDefaultQuota = (role, quota, value) ->
        return $scope.settings[role][quota] != value

    $scope.showUserSearch = () ->
        $scope.UserSearchVisible = true

    $scope.findUsers = (q) ->
        role = $scope.tabs[$scope.activeTab]
        return $http.post("/api/lmn/ldap-search", {role:role, login:q}).then (resp) ->
            return resp.data

    $scope.changeUser = (role, login, quota) ->
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

    $scope.changeGroup = (type, group, quota) ->
        delete $scope.groupsToChange[type][group+"_"+quota]
        ## Default value for a quota in sophomorix
        value = '---'
        if $scope.groupquota[type][group]['QUOTA'][quota].value != 0
            value = $scope.groupquota[type][group]['QUOTA'][quota].value
        $scope.groupsToChange[type][group+"_"+quota] = {
            'group': group,
            'quota': quota,
            'type': type,
            'value': value
        }

    $scope.resetClass = (cl) ->
        for share in $scope.groupquota_types
            $scope.groupquota['adminclass'][cl]['QUOTA'][share.type].value = 0
            $scope.changeGroup('adminclass', cl, share.type)

    $scope.resetProject = (pr) ->
        for share in $scope.groupquota_types
            $scope.groupquota['project'][pr]['QUOTA'][share.type].value = 0
            $scope.changeGroup('project', pr, share.type)

    $scope.remove = (role, user) ->
        ## Reset all 3 quotas to default
        $scope.non_default[role][user.login]['QUOTA'] = angular.copy($scope.settings['role.'+role])
        $scope.changeUser(role, user.login, 'QUOTA_DEFAULT_GLOBAL')
        $scope.changeUser(role, user.login, 'QUOTA_DEFAULT_SCHOOL')
        $scope.changeUser(role, user.login, 'MAILQUOTA_DEFAULT')
        delete $scope.non_default[role][user.login]
        $scope.non_default[role].list.splice($scope.non_default[role].list.indexOf(user),1)

    $scope.saveApply = () ->
        wait.modal(gettext("Saving quotas ..."), 'progressbar')
        $http.post('/api/lmn/quota/save', {users: $scope.toChange, groups: $scope.groupsToChange}).then () ->
            $rootScope.$emit('updateWaiting', 'done')
            $uibModal.open(
                templateUrl: '/lmn_quotas:resources/partial/apply.modal.html'
                controller: 'LMQuotasApplyModalController'
                backdrop: 'static'
            )

    hotkeys.on $scope, (key, event) ->
        current_tab = $scope.tabs[$scope.activeTab]
        if (key == 'F' && event.ctrlKey)
            if $scope.activeTab <= 2
                $scope.showUserSearch()
                return true
            return false

        if (key == 'S' && event.ctrlKey)
            $scope.saveApply()
            return true

        return false