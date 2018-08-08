angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/schooladmins',
        controller: 'LMUsersSchooladminsController'
        templateUrl: '/lm_users:resources/partial/schooladmins.html'


angular.module('lm.users').controller 'LMUsersSchooladminsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Schooladmins'))

    $http.get("/api/lm/sophomorixUsers/schooladmins").then (resp) ->
        console.log('schooladmins')
        $scope.schooladmins = resp.data

    $scope.showInitialPassword = (user) ->
       $http.post('/api/lm/users/password', {user: ( x['sAMAccountName'] for x in user ), action: 'get'}).then (resp) ->
          messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (user) ->
       $http.post('/api/lm/users/password', {user: ( x['sAMAccountName'] for x in user ), action: 'set-initial'}).then (resp) ->
          notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
       $http.post('/api/lm/users/password', {user: ( x['sAMAccountName'] for x in user ), action: 'set-random'}).then (resp) ->
          notify.success gettext('Random password set')

    $scope.setCustomPassword = (user) ->
       $uibModal.open(
          templateUrl: '/lm_users:resources/partial/customPassword.modal.html'
          controller: 'LMNUsersCustomPasswordController'
          size: 'mg'
          resolve:
             users: () -> user
       )

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




