'use strict';

angular.module('lmn.permissions', ['core']);


'use strict';

angular.module('lmn.permissions').config(function ($routeProvider) {
    $routeProvider.when('/view/permissions', {
        templateUrl: '/lmn_permissions:resources/partial/index.html',
        controller: 'PermissionListIndexController'
    });
});


// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lmn.permissions').controller('PermissionListIndexController', function($scope, $http, $interval, $timeout, notify, pageTitle, messagebox, gettext, config) {
    pageTitle.set(gettext('List all permissions'));
    $scope.query = {
      'plugin': '',
      'sidebar': ''
    };
    $scope.columns = ['globaladministrator', 'schooladministrator', 'teacher', 'student', 'default'];
    $scope.roles = ['globaladministrator', 'schooladministrator', 'teacher', 'student'];
    $http.get('/api/permissions').then(function(resp) {
      $scope.pluginObj = resp.data[0];
      // To iterate in alphabetical order
      $scope.pluginList = Object.keys($scope.pluginObj);
      $scope.pluginList.sort();
      $scope.apiPermissions = resp.data[1];
      $scope.sidebarPermissions = resp.data[2];
      // To iterate in alphabetical order
      $scope.sidebarPermissionsList = Object.keys($scope.sidebarPermissions);
      return $scope.sidebarPermissionsList.sort();
    });
    $scope.get_provider = function(url) {
      if (url.includes('/lm')) {
        return "Linuxmuster.net";
      }
      if (url.includes('/ni')) {
        return "Netzint";
      }
      return "Ajenti";
    };
    $scope.label_color = function(provider) {
      if (provider === "Linuxmuster.net") {
        return "warning";
      }
      if (provider === "Netzint") {
        return "info";
      }
      if (provider === "Ajenti") {
        return "default";
      }
    };
    $scope.iconify = function(bool) {
      if (typeof bool === "undefined") {
        return 'question';
      }
      if (bool === "true") {
        return 'check';
      }
      return 'times';
    };
    $scope.colorize = function(bool) {
      if (typeof bool === "undefined") {
        return '';
      }
      if (bool === "true") {
        return 'color:green';
      }
      return 'color:red';
    };
    $scope.count_rows = function(plugin) {
      return document.getElementById('table_' + plugin).rows.length > 1;
    };
    $scope.switch = function(obj, role) {
      // Set the filter to role
      // obj may be plugin or sidebar
      if ($scope.query[obj] === role) {
        return $scope.query[obj] = '';
      } else {
        return $scope.query[obj] = role;
      }
    };
    $scope.changeApi = function(details, role) {
      var state, states;
      state = $scope.apiPermissions[details.permission_id][role];
      // Cycle undefined -> false -> true
      states = [void 0, "false", "true"];
      return $scope.apiPermissions[details.permission_id][role] = states[(states.indexOf(state) + 1) % 3];
    };
    $scope.changeSidebar = function(url, role) {
      var state, states;
      state = $scope.sidebarPermissions[url][role];
      // Cycle undefined -> false -> true
      states = [void 0, "false", "true"];
      return $scope.sidebarPermissions[url][role] = states[(states.indexOf(state) + 1) % 3];
    };
    $scope.filter_sidebar = function(url) {
      var details;
      details = $scope.sidebarPermissions[url];
      if ($scope.roles.indexOf($scope.query.sidebar) !== -1) {
        return details[$scope.query.sidebar] === "true";
      } else {
        return url.includes($scope.query.sidebar);
      }
      return true;
    };
    $scope.filter_plugin = function(plugin) {
      if ($scope.roles.indexOf($scope.query.plugin) !== -1) {
        return true;
      }
      return plugin.includes($scope.query.plugin);
    };
    $scope.filter_api = function(details) {
      if ($scope.roles.indexOf($scope.query.plugin) !== -1) {
        if (details.permission_id) {
          return $scope.apiPermissions[details.permission_id][$scope.query.plugin] === "true";
        } else {
          return false;
        }
      }
      return true;
    };
    return $scope.export = function() {
      return $http.post('/api/permissions/export', {
        'api': $scope.apiPermissions,
        'sidebar': $scope.sidebarPermissions
      }).then(function(resp) {
        return location.href = '/api/permissions/download/' + resp.data;
      });
    };
  });

}).call(this);

