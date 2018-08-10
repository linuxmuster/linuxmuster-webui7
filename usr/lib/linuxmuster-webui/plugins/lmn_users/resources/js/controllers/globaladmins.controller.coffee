angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/globaladmins',
        controller: 'LMUsersGloballadminsController'
        templateUrl: '/lm_users:resources/partial/globaladmins.html'

angular.module('lm.users').controller 'LMUsersGloballadminsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Globalladmins'))

    $scope.sorts = [
     {
       name: gettext('Login')
       fx: (x) -> x.sAMAccountName
     }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
     page: 1
     pageSize: 50


    $http.get("/api/lm/sophomorixUsers/globaladmins").then (resp) ->
        $scope.globaladmins = resp.data

    $scope.showInitialPassword = (user) ->
      $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'get'}).then (resp) ->
        messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (user) ->
      $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'set-initial'}).then (resp) ->
        notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
      $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'set-random'}).then (resp) ->
        notify.success gettext('Random password set')

    $scope.setCustomPassword = (user) ->
      $uibModal.open(
        templateUrl: '/lm_users:resources/partial/customPassword.modal.html'
        controller: 'LMNUsersCustomPasswordController'
        size: 'mg'
        resolve:
          users: () -> user
      )

    $scope.addGlobalAdmin = () ->
      $uibModal.open(
        templateUrl: '/lm_users:resources/partial/addAdmin.modal.html'
        controller: 'LMNUsersAddAdminController'
        size: 'mg'
        resolve:
          role: () -> angular.copy('global-admin')
      )

    $scope.haveSelection = () ->
        if $scope.globaladmins
            for x in $scope.globaladmins
                if x.selected
                    return true
        return false

    $scope.batchSetInitialPassword = () ->
        $scope.setInitialPassword((x for x in $scope.globaladmins when x.selected))

    $scope.batchSetRandomPassword = () ->
        $scope.setRandomPassword((x for x in $scope.globaladmins when x.selected))

    $scope.batchSetCustomPassword = () ->
        $scope.setCustomPassword((x for x in $scope.globaladmins when x.selected))

    $scope.selectAll = () ->
        for globaladmin in $scope.globaladmins
            globaladmin.selected = true




