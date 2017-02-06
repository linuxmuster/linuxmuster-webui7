angular.module('lm.auth').config ($routeProvider) ->
    $routeProvider.when '/view/lm/change-password',
        controller: 'LMPasswordChangeCtrl'
        templateUrl: '/lm_auth:resources/partial/index.html'


angular.module('lm.auth').controller 'LMPasswordChangeCtrl', ($scope, $http, pageTitle, gettext, notify) ->
    pageTitle.set(gettext('Change Password'))

    $scope.change = () ->
        if not $scope.newPassword or not $scope.password
            return
        if $scope.newPassword != $scope.newPassword2
            notify.error gettext('Passwords do not match')
            return

        $http.post('/api/lm/change-password', password: $scope.password, new_password: $scope.newPassword).then () ->
            notify.success gettext('Password changed')
        .catch (e) ->
            notify.error gettext('Password change failed')
