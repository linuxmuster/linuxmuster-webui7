angular.module('lm.users').controller 'LMUsersCheckResultsModalController', ($scope, $uibModalInstance, $uibModal, data) ->
    $scope.data = data
    $scope._ = {
        doAdd: data['SUMMARY'][1]['ADD']['RESULT'] > 0
        doMove: data['SUMMARY'][2]['UPDATE']['RESULT'] > 0
        doKill: data['SUMMARY'][3]['KILL']['RESULT'] > 0
    }

    $scope.apply = () ->
        $uibModalInstance.close()
        msg = $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/apply.modal.html'
            controller: 'LMUsersApplyModalController'
            backdrop: 'static'
            size: 'lg'
            resolve:
                params: () -> $scope._
        )

        $uibModalInstance.close()

    $scope.cancel = () ->
        $uibModalInstance.dismiss()


angular.module('lm.users').controller 'LMUsersApplyModalController', ($scope, $uibModalInstance, $http, $route, gettext, notify, params) ->
    $scope.options = {
       autoscroll: true
    }

    $scope.close = () ->
        $uibModalInstance.close()

    $scope.isWorking = true
    $http.post('/api/lm/users/apply', params).then (resp) ->
        $scope.isWorking = false
        notify.success gettext('Changes applied')
        $route.reload()

    .catch (resp) ->
        $scope.isWorking = false
        notify.error gettext('Failed'), resp.data.message



angular.module('lm.users').controller 'LMUsersCheckModalController', ($scope, $http, notify, $uibModalInstance, $uibModal, gettext) ->
    $scope.isWorking = true

    $http.get('/api/lm/users/check').then (resp) ->
        if resp.data['OUTPUT'][0]['TYPE']  is 'ERROR'
            notify.error gettext('Check failed'), resp.data.message
            $scope.isWorking = false
            $scope.error = true
            $scope.errorMessage = resp.data['OUTPUT'][0]['MESSAGE_EN']
        else
            $scope.showCheckResults(resp.data)
            $uibModalInstance.close()
    .catch (resp) ->
        $scope.isWorking = false
        $scope.error = true
        notify.error gettext('Check failed'), resp.data.message

    $scope.showCheckResults = (data) ->
        $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/result.modal.html'
            controller: 'LMUsersCheckResultsModalController'
            resolve:
                data: () -> data
        )
        console.log(data)

    $scope.close = () ->
        $uibModalInstance.close()
