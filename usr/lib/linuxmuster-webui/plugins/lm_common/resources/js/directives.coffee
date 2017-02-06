angular.module('lm.common').directive 'lmLog', ($http, $interval, $timeout) ->
    return {
        restrict: 'E'
        scope: {
            path: '='
            lines: '=?'
        }
        template: '''
            <pre style="max-height: 200px; overflow-y: scroll" ng:bind="visibleContent"></pre>
        '''
        link: ($scope, element) ->
            $scope.content = ''
            i = $interval () ->
                $http.get("/api/lm/log#{$scope.path}?offset=#{$scope.content.length}").then (resp) ->
                    $scope.content += resp.data

                    $scope.visibleContent = $scope.content
                    if $scope.lines
                        lines = $scope.content.split('\n')
                        console.log lines, lines[lines.length - 1]
                        if lines[lines.length - 1] == ''
                            lines = lines[...-1]
                        lines = lines[-$scope.lines..]
                        console.log lines
                        $scope.visibleContent = lines.join('\n')

                    $timeout () ->
                        e = $(element).find('pre')[0]
                        e.scrollTop = e.scrollHeight
            , 1000

            $scope.$on '$destroy', () ->
                $interval.cancel(i)
    }
