angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/schooladmins',
        controller: 'LMUsersSchooladminsController'
        templateUrl: '/lm_users:resources/partial/schooladmins.html'


angular.module('lm.users').controller 'LMUsersSchooladminsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Schooladmins'))

    $http.get("/api/lm/sophomorixUsers/schooladmins").then (resp) ->
        $scope.schooladmins = resp.data


## legacy functions
    $scope.showInitialPassword = (schooladmins) ->
        $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in schooladmins), action: 'get'}).then (resp) ->
            messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (schooladmins) ->
        $http.post('/api/lm/sophomorixUsers/password', {users: (x.sAMAccountName for x in schooladmins), action: 'set-initial'}).then (resp) ->
            notify.success gettext('Initial password set')

    $scope.setRandomPassword = (schooladmins) ->
        $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in schooladmins), action: 'set-random'}).then (resp) ->
            text = ("#{x.user}: #{x.password}" for x in resp.data).join(',\n')
            messagebox.show(title: gettext('New password'), text: text, positive: 'OK')

    $scope.setCustomPassword = (schooladmins) ->
        messagebox.prompt(gettext('New password')).then (msg) ->
            if not msg.value
                return
            $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in schooladmins), action: 'set', password: msg.value}).then (resp) ->
                notify.success gettext('New password set')

    $scope.haveSelection = () ->
        if $scope.schooladmins
            for x in $scope.schooladmins
                if x.selected
                    return true
        return false

    $scope.batchSetInitialPassword = () ->
        $scope.setInitialPassword((x for x in $scope.schooladmins when x.selected))

    $scope.batchSetRandomPassword = () ->
        $scope.setRandomPassword((x for x in $scope.schooladmins when x.selected))

    $scope.batchSetCustomPassword = () ->
        $scope.setCustomPassword((x for x in $scope.schooladmins when x.selected))

    $scope.selectAll = () ->
        for schooladmin in $scope.schooladmins
            schooladmin.selected = true




