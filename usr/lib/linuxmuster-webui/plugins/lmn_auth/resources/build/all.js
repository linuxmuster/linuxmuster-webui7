// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lmn.auth', ['core']);

  angular.module('lmn.auth').run(function(customization, $http, identity, gettextCatalog, config) {
    var lang;
    lang = config.data.language || 'en';
    return $http.get(`/resources/all.locale.js?lang=${lang}`).then(function(rq) {
      var expr;
      gettextCatalog.setStrings(lang, rq.data);
      expr = rq.data['Change password'];
      return customization.plugins.core.extraProfileMenuItems = [
        {
          url: '/view/lmn/change-password',
          name: expr,
          icon: 'key'
        }
      ];
    });
  });

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lmn.auth').config(function($routeProvider) {
    return $routeProvider.when('/view/lmn/change-password', {
      controller: 'LMNPasswordChangeCtrl',
      templateUrl: '/lmn_auth:resources/partial/index.html'
    });
  });

  angular.module('lmn.auth').controller('LMNPasswordChangeCtrl', function($scope, $http, pageTitle, gettext, notify, validation) {
    pageTitle.set(gettext('Change Password'));
    return $scope.change = function() {
      var test;
      if (!$scope.newPassword || !$scope.password) {
        return;
      }
      if ($scope.newPassword !== $scope.newPassword2) {
        notify.error(gettext('Passwords do not match'));
        return;
      }
      test = validation.isValidPassword($scope.newPassword);
      if (test !== true) {
        notify.error(gettext(test));
        return;
      }
      return $http.post('/api/lmn/change-password', {
        password: $scope.password,
        new_password: $scope.newPassword
      }).then(function() {
        notify.success(gettext('Password changed'));
        return window.location.replace('landingpage');
      }).catch(function(e) {
        return notify.error(gettext('Password change failed'));
      });
    };
  });

}).call(this);

