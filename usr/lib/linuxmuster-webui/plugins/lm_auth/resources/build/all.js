(function() {
  angular.module('lm.auth', ['core']);

  angular.module('lm.auth').run(function(customization, identity) {
    return customization.plugins.core.extraProfileMenuItems = [
      {
        url: '/view/lm/change-password',
        name: 'Change password',
        icon: 'key'
      }
    ];
  });

}).call(this);

(function() {
  angular.module('lm.auth').config(function($routeProvider) {
    return $routeProvider.when('/view/lm/change-password', {
      controller: 'LMPasswordChangeCtrl',
      templateUrl: '/lm_auth:resources/partial/index.html'
    });
  });

  angular.module('lm.auth').controller('LMPasswordChangeCtrl', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Change Password'));
    return $scope.change = function() {
      if (!$scope.newPassword || !$scope.password) {
        return;
      }
      if ($scope.newPassword !== $scope.newPassword2) {
        notify.error(gettext('Passwords do not match'));
        return;
      }
      return $http.post('/api/lm/change-password', {
        password: $scope.password,
        new_password: $scope.newPassword
      }).then(function() {
        return notify.success(gettext('Password changed'));
      })["catch"](function(e) {
        return notify.error(gettext('Password change failed'));
      });
    };
  });

}).call(this);
