angular.module('lmn.common').controller 'lmWaitController', ($scope, $rootScope, $uibModalInstance, status, style) ->
    $scope.status = status
    $scope.style = style

    $rootScope.$on 'updateWaiting', (event, data) ->
        if data == 'done'
            $uibModalInstance.dismiss()

angular.module('lmn.common').service 'wait', ($uibModal) ->

    this.modal = (status, style) ->
        $uibModal.open(
            template: """
                <div class=\"modal-header\">
                    <h4 translate>{{status}}</h4>
                </div>

                <div class=\"modal-body\">
                    <div ng:show=\"style == 'spinner'\"><progress-spinner></progress-spinner></div>
                    <div ng:show=\"style == 'progressbar'\">
                        <uib-progressbar style=\"height: 10px;\" type=\"warning\" max=\"100\" value=\"100 * value / max\" ng:class=\"{indeterminate: !max}\">
                    </uib-progressbar>
                    </div>
                </div>
            """
            controller: 'lmWaitController'
            backdrop: 'static',
            keyboard: false
            size: 'mg'
            resolve:
                status: () -> status
                style: () -> style
        )

    return this
