angular.module('lmn.landingpage').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/landingpage',
        controller: 'LMNLandingController'
        templateUrl: '/lmn_landingpage:resources/partial/index.html'

angular.module('lmn.landingpage').controller 'LMNLandingController', ($scope, $http, $uibModal, $location, gettext, notify, pageTitle, messagebox) ->
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
           return
        $scope.getUser($scope.identity.user)
        return

    $scope.getQuota = $http.post('/api/lmn/quota/').then (resp) ->
            $scope.used = resp.data.used;
            $scope.total = resp.data.total;
            $scope.usage = Math.floor((100 * $scope.used) / $scope.total);

    $scope.changePassword = () ->
        $location.path('/view/lmn/change-password');
