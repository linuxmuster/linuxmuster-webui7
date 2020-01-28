angular.module('lm.common').controller 'lmWaitController', ($scope, $rootScope, $uibModalInstance) ->

    $rootScope.$on 'updateWaiting', (event, data) ->
        if data == 'done'
            $uibModalInstance.dismiss()
