angular.module('lmn.landingpage').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/landingpage',
        controller: 'LMNLandingController'
        templateUrl: '/lmn_landingpage:resources/partial/index.html'

angular.module('lmn.landingpage').controller 'LMNLandingController', ($scope, $http, $uibModal, gettext, notify, pageTitle, messagebox) ->
    pageTitle.set(gettext('Home'))

    $scope.getUser = (username) ->
            $http.post('/api/lm/sophomorixUsers/students', {action: 'get-specified', user: username}).then (resp) ->
                    $scope.user = resp.data[0]
                    console.log ($scope.user)

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
           return
        if $scope.identity.user is null
           return
        if $scope.identity.user is 'root'
           # $scope.identity.user = 'hulk'
           # $scope.getUser($scope.identity.user)
           return
        $scope.getUser($scope.identity.user)
        return

    isStrongPwd = (password) ->
          regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}/
          validPassword = regExp.test(password)
          return validPassword

    validCharPwd =(password) ->
        regExp = /^[a-zA-Z0-9!@#§+\-$%&*{}()\]\[]+$/
        validPassword = regExp.test(password)
        return validPassword;

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
            
    $scope.getQuota = (username) -> 
        $http.post('/api/lmn/quota/' + username).then (resp) ->
            $scope.used = resp.data.used;
            $scope.total = resp.data.total;
            $scope.usage = Math.floor((100 * $scope.used) / $scope.total);
    $scope.getQuota($scope.identity.user)
