angular.module('lm.common').controller 'lmWaitController', ($scope, $rootScope, $uibModalInstance, status, style) ->
    $scope.status = status
    $scope.style = style

    $rootScope.$on 'updateWaiting', (event, data) ->
        if data == 'done'
            $uibModalInstance.dismiss()
