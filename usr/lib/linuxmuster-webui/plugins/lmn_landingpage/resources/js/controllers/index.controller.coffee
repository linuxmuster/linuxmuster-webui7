angular.module('lmn.landingpage').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/landingpage',
        controller: 'LMNLandingController'
        templateUrl: '/lmn_landingpage:resources/partial/index.html'

angular.module('lmn.landingpage').controller 'LMNLandingController', ($scope, $http, $uibModal, gettext, notify, pageTitle, messagebox) ->
    pageTitle.set(gettext('Home'))

    $scope.getUser = (username) ->
            $http.post('/api/lm/sophomorixUsers/students', {action: 'get-specified', user: username}).then (resp) ->
                    $scope.user = resp.data[0]
                    console.log ($scope.user)

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
           return
        if $scope.identity.user is null
           return
        if $scope.identity.user is 'root'
           # $scope.identity.user = 'hulk'
           # $scope.getUser($scope.identity.user)
           return
        $scope.getUser($scope.identity.user)
        return
