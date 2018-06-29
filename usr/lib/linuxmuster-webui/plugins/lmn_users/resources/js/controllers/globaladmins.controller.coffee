angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/globaladmins',
        controller: 'LMUsersSchooladminsController'
        templateUrl: '/lm_users:resources/partial/globaladmins.html'


angular.module('lm.users').controller 'LMUsersSchooladminsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Schooladmins'))

    $http.get("/api/lm/sophomorixUsers/globaladmins").then (resp) ->
        $scope.globaladmins = resp.data

    $scope.showInitialPassword = (user) ->
      username = (user[0]['sAMAccountName'])
      $http.post('/api/lm/users/password', {user: username, action: 'get'}).then (resp) ->
        messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (user) ->
      console.log (user)
      username = (user[0]['sAMAccountName'])
      $http.post('/api/lm/users/password', {user: username, action: 'set-initial'}).then (resp) ->
        notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
      console.log (user)
      username = (user[0]['sAMAccountName'])
      $http.post('/api/lm/users/password', {user: username, action: 'set-random'}).then (resp) ->
        notify.success gettext('Random password set')

    $scope.setCustomPassword = (user) ->
      $uibModal.open(
        templateUrl: '/lm_users:resources/partial/customPassword.modal.html'
        controller: 'LMNUsersCustomPasswordController'
        size: 'mg'
        resolve:
          user: () -> user
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




