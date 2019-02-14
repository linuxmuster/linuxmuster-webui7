angular.module('lm.auth').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/change-password',
        controller: 'LMNPasswordChangeCtrl'
        templateUrl: '/lm_auth:resources/partial/index.html'

isStrongPwd = (password) ->
      regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}/
      validPassword = regExp.test(password)
      return validPassword

validCharPwd =(password) ->
    regExp = /^[a-zA-Z0-9!@#§+\-$%&*{}()\]\[]+$/
    validPassword = regExp.test(password)
    return validPassword;


angular.module('lm.auth').controller 'LMNPasswordChangeCtrl', ($scope, $http, pageTitle, gettext, notify) ->
    pageTitle.set(gettext('Change Password'))

    $scope.change = () ->
        if not $scope.newPassword or not $scope.password
            return
        if $scope.newPassword != $scope.newPassword2
            notify.error gettext('Passwords do not match')
            return
        if not validCharPwd($scope.newPassword)
           notify.error gettext("Password contains invalid characters")
           return
        if not isStrongPwd($scope.newPassword)
           notify.error gettext("Password too weak")
           return


        $http.post('/api/lmn/change-password', password: $scope.password, new_password: $scope.newPassword).then () ->
            notify.success gettext('Password changed')
            window.location.replace('landingpage')
        .catch (e) ->
            notify.error gettext('Password change failed')
