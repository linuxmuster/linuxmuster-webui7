angular.module('lm.users').controller 'LMNUserDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, id) ->

    #notify.error gettext("You have to enter a username")
    $scope.id = id

    $http.post('/api/lm/sophomorixUsers/students', {action: 'get-specified', user: id}).then (resp) ->
        $scope.students = resp.data
        console.log $scope.students

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
