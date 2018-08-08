isStrongPwd1 = (password) ->
      regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}/
      validPassword = regExp.test(password)
      return validPassword


angular.module('lm.users').controller 'LMNUsersCustomPasswordController', ($scope, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, users) ->
    console.log (users)
    #$scope.username = users: (x['sAMAccountName'] for x in users)
    $scope.username = users
    $scope.save = (userpw) ->
        if not $scope.userpw
            notify.error gettext("You have to enter a password")
            return
        if not isStrongPwd1($scope.userpw)
           notify.error gettext("Password too weak")
           return
        else
            $http.post('/api/lm/users/password', {users: (x['sAMAccountName'] for x in users), action: 'set', password: $scope.userpw}).then (resp) ->
                notify.success gettext('New password set')
        $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()

