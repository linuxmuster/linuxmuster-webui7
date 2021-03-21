angular.module('lmn.wdatetime').controller 'lm.wdatetime', ($scope) ->
    # $scope.widget is our widget descriptor here
    $scope.$on 'widget-update', ($event, id, data) ->
        if id != $scope.widget.id
            return
        $scope.value = data


angular.module('lmn.wdatetime').controller 'lm.wdatetimeconfig', ($scope) ->
    # $scope.configuredWidget is our widget descriptor here
    $scope.configuredWidget.config.format ?= "%d.%m.%Y %H:%M"
