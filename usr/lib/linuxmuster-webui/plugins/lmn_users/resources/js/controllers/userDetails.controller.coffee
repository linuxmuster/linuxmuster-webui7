angular.module('lm.users').controller 'LMNUserDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, id, role) ->

    #notify.error gettext("You have to enter a username")
    $scope.id = id
    console.log ($scope.id)

    $http.post('/api/lm/sophomorixUsers/'+role, {action: 'get-specified', user: id}).then (resp) ->
        $scope.userDetails = resp.data
        console.log $scope.userDetails

    #$scope.save = (username) ->
    #    if not $scope.username
    #        notify.error gettext("You have to enter a username")
    #        return
    #    else
    #        notify.success gettext('Adding administrator...')
    #        $http.post('/api/lm/users/change-'+role, {action: 'create' ,users: username}).then (resp) ->
    #            notify.success gettext('Administrator added')
    #            $route.reload()
    #        $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()
