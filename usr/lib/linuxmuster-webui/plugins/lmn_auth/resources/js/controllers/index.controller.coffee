angular.module('lmn.auth').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/change-password',
        controller: 'LMNPasswordChangeCtrl'
        templateUrl: '/lmn_auth:resources/partial/index.html'

angular.module('lmn.auth').controller 'LMNPasswordChangeCtrl', ($scope, $http, pageTitle, gettext, notify, validation) ->
    pageTitle.set(gettext('Change Password'))

    $scope.showNewPassword = false;

    $scope.toggleShowNewPassword = () => $scope.showNewPassword = !$scope.showNewPassword;

    $scope.change = () ->
        test = validation.isValidPassword($scope.newPassword)
        if test != true
           notify.error gettext(test)
           return


        $http.post('/api/lmn/change-password', password: $scope.password, new_password: $scope.newPassword).then () ->
            notify.success gettext('Password changed')
            window.location.replace('landingpage')
        .catch (e) ->
            notify.error(gettext('Password change failed: ') + e.data.message)
