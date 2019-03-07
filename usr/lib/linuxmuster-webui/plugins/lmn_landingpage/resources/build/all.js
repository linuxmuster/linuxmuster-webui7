// Generated by CoffeeScript 2.3.2
(function() {
  angular.module('lmn.landingpage', ['core', 'lm.common']);

}).call(this);

// Generated by CoffeeScript 2.3.2
(function() {
  angular.module('lmn.landingpage').config(function($routeProvider) {
    return $routeProvider.when('/view/lmn/landingpage', {
      controller: 'LMNLandingController',
      templateUrl: '/lmn_landingpage:resources/partial/index.html'
    });
  });

  angular.module('lmn.landingpage').controller('LMNLandingController', function($scope, $http, $uibModal, $location, gettext, notify, pageTitle, messagebox) {
    pageTitle.set(gettext('Home'));
    $scope.getUser = function(username) {
      return $http.post('/api/lm/sophomorixUsers/students', {
        action: 'get-specified',
        user: username
      }).then(function(resp) {
        $scope.user = resp.data[0];
        return console.log($scope.user);
      });
    };
    $scope.$watch('identity.user', function() {
      if ($scope.identity.user === void 0) {
        return;
      }
      if ($scope.identity.user === null) {
        return;
      }
      if ($scope.identity.user === 'root') {
        return;
      }
      // $scope.identity.user = 'hulk'
      // $scope.getUser($scope.identity.user)
      $scope.getUser($scope.identity.user);
    });
    $scope.getQuota = $http.post('/api/lmn/quota/').then(function(resp) {
      $scope.used = resp.data.used;
      $scope.total = resp.data.total;
      return $scope.usage = Math.floor((100 * $scope.used) / $scope.total);
    });
    return $scope.changePassword = function() {
      return $location.path('/view/lmn/change-password');
    };
  });

}).call(this);

