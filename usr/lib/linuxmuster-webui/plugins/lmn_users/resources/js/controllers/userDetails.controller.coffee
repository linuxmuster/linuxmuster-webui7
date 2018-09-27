angular.module('lm.users').controller 'LMNUserDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, id, role) ->

    #notify.error gettext("You have to enter a username")
    $scope.id = id

    $http.post('/api/lm/sophomorixUsers/'+role, {action: 'get-specified', user: id}).then (resp) ->
        $scope.userDetails = resp.data

    $scope.close = () ->
        $uibModalInstance.dismiss()
