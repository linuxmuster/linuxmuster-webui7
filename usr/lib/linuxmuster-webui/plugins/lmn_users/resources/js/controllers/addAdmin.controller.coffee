angular.module('lm.users').controller 'LMNUsersAddAdminController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, role) ->

    $scope.role = role
    console.log ('test')
    $scope.save = (username) ->
        if not $scope.username
            notify.error gettext("You have to enter a username")
            return
        else
            notify.success gettext('Adding administrator...')
            $http.post('/api/lm/users/add-'+role, {user: username}).then (resp) ->
                notify.success gettext('Administrator added')
                $route.reload()
            $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()

