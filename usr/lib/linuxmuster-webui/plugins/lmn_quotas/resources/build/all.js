// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lmn.quotas', ['core', 'lmn.common']);

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lmn.quotas').config(function($routeProvider) {
    $routeProvider.when('/view/lmn/quotas', {
      controller: 'LMQuotasController',
      templateUrl: '/lmn_quotas:resources/partial/index.html'
    });
    return $routeProvider.when('/view/lmn/quotas-disabled', {
      templateUrl: '/lmn_quotas:resources/partial/disabled.html'
    });
  });

  angular.module('lmn.quotas').controller('LMQuotasApplyModalController', function($scope, $http, $uibModalInstance, $window, gettext, notify) {
    $scope.logVisible = true;
    $scope.isWorking = true;
    $http.post('/api/lmn/quota/apply').then(function() {
      $scope.isWorking = false;
      return notify.success(gettext('Update complete'));
    }).catch(function(resp) {
      notify.error(gettext('Update failed'), resp.data.message);
      $scope.isWorking = false;
      return $scope.logVisible = true;
    });
    return $scope.close = function() {
      $uibModalInstance.close();
      return $window.location.reload();
    };
  });

  angular.module('lmn.quotas').controller('LMQuotasController', function($scope, $http, $uibModal, $location, $q, gettext, hotkeys, lmEncodingMap, notify, pageTitle, lmFileBackups, $rootScope, wait) {
    pageTitle.set(gettext('Quotas'));
    $scope.UserSearchVisible = false;
    $scope.tabs = ['student', 'teacher', 'schooladministrator', 'schoolclass', 'project', 'quota_check'];
    $scope.quota_check_init = function() {
      $scope.show_table_user_quota_check = false;
      $scope.checking_quota_user = false;
      $scope._.quota_user_check = '';
      $scope.user_directories = {};
      return $scope.user_total_size = 0;
    };
    $scope.clearQuotaCheckSelect = function() {
      return $scope._.quota_user_check = '';
    };
    $scope.toChange = {
      'teacher': {},
      'student': {},
      'schooladministrator': {}
    };
    $scope.groupsToChange = {
      'adminclass': {},
      'project': {}
    };
    $scope._ = {
      addNewSpecial: null,
      quota_user_check: ''
    };
    $scope.searchText = gettext('Search user by login, firstname or lastname (min. 3 chars)');
    // Need an array to keep the order ...
    $scope.quota_types = [
      {
        'type': 'QUOTA_DEFAULT_GLOBAL',
        'name': gettext('Quota default global (MiB)')
      },
      {
        'type': 'QUOTA_DEFAULT_SCHOOL',
        'name': gettext('Quota default school (MiB)')
      },
      {
        'type': 'CLOUDQUOTA_PERCENTAGE',
        'name': gettext('Cloudquota (%)')
      },
      {
        'type': 'MAILQUOTA_DEFAULT',
        'name': gettext('Mailquota default (MiB)')
      }
    ];
    $scope.groupquota_types = [
      {
        'type': 'linuxmuster-global',
        'classname': gettext('Quota default global (MiB)'),
        'projname': gettext('Add to default global (MiB)')
      },
      {
        'type': 'default-school',
        'classname': gettext('Quota default school (MiB)'),
        'projname': gettext('Add to default school (MiB)')
      },
      {
        'type': 'mailquota',
        'classname': gettext('Mailquota default (MiB)'),
        'projname': gettext('Add to mailquota (MiB)')
      }
    ];
    $scope.groupquota = 0;
    $scope.get_class_quota = function() {
      if (!$scope.groupquota) {
        wait.modal(gettext("Retrieving groups quotas ..."), 'progressbar');
        return $http.get('/api/lmn/quota/groups').then(function(resp) {
          $scope.groupquota = resp.data;
          return $rootScope.$emit('updateWaiting', 'done');
        });
      }
    };
    $http.get('/api/lmn/quota/quotas').then(function(resp) {
      $scope.non_default = resp.data[0];
      return $scope.settings = resp.data[1];
    });
    $scope.$watch('_.addNewSpecial', function() {
      var user;
      if ($scope._.addNewSpecial) {
        user = $scope._.addNewSpecial;
        $scope.non_default[user.role][user.login] = {
          'QUOTA': angular.copy($scope.settings['role.' + user.role]),
          'displayName': user.displayName
        };
        $scope.non_default[user.role].list.push({
          'sn': user.sn,
          'login': user.login,
          'givenname': user.givenName
        });
        $scope._.addNewSpecial = null;
        $scope.UserSearchVisible = false;
        return notify.success(user.displayName + gettext(" added with default values in the list."));
      }
    });
    $scope.isDefaultQuota = function(role, quota, value) {
      return $scope.settings[role][quota] !== value;
    };
    $scope.showUserSearch = function() {
      return $scope.UserSearchVisible = true;
    };
    $scope.findUsers = function(q) {
      var role;
      role = '';
      if ($scope.activeTab < 3) {
        role = $scope.tabs[$scope.activeTab];
      }
      return $http.post("/api/lmn/ldap-search", {
        role: role,
        login: q
      }).then(function(resp) {
        return resp.data;
      });
    };
    $scope.quota_check = function() {
      if (!$scope._.quota_user_check) {
        return;
      }
      $scope.checking_quota_user = true;
      $scope.show_table_user_quota_check = false;
      return $http.get(`/api/lmn/quota/check/${$scope._.quota_user_check.login}`).then(function(resp) {
        $scope.checking_quota_user = false;
        $scope.show_table_user_quota_check = true;
        $scope.user_directories = resp.data[0];
        return $scope.user_total_size = resp.data[1];
      });
    };
    $scope.changeUser = function(role, login, quota) {
      var value;
      delete $scope.toChange[role][login + "_" + quota];
      //# Default value for a quota in sophomorix
      value = '---';
      if ($scope.non_default[role][login]['QUOTA'][quota] !== $scope.settings['role.' + role][quota]) {
        value = $scope.non_default[role][login]['QUOTA'][quota];
      }
      return $scope.toChange[role][login + "_" + quota] = {
        'login': login,
        'quota': quota,
        'value': value
      };
    };
    $scope.changeGroup = function(type, group, quota) {
      var value;
      delete $scope.groupsToChange[type][group + "_" + quota];
      //# Default value for a quota in sophomorix
      value = '---';
      if ($scope.groupquota[type][group]['QUOTA'][quota].value !== 0) {
        value = $scope.groupquota[type][group]['QUOTA'][quota].value;
      }
      return $scope.groupsToChange[type][group + "_" + quota] = {
        'group': group,
        'quota': quota,
        'type': type,
        'value': value
      };
    };
    $scope.resetClass = function(cl) {
      var i, len, ref, results, share;
      ref = $scope.groupquota_types;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        share = ref[i];
        $scope.groupquota['adminclass'][cl]['QUOTA'][share.type].value = 0;
        results.push($scope.changeGroup('adminclass', cl, share.type));
      }
      return results;
    };
    $scope.resetProject = function(pr) {
      var i, len, ref, results, share;
      ref = $scope.groupquota_types;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        share = ref[i];
        $scope.groupquota['project'][pr]['QUOTA'][share.type].value = 0;
        results.push($scope.changeGroup('project', pr, share.type));
      }
      return results;
    };
    $scope.remove = function(role, user) {
      //# Reset all 3 quotas to default
      $scope.non_default[role][user.login]['QUOTA'] = angular.copy($scope.settings['role.' + role]);
      $scope.changeUser(role, user.login, 'QUOTA_DEFAULT_GLOBAL');
      $scope.changeUser(role, user.login, 'QUOTA_DEFAULT_SCHOOL');
      $scope.changeUser(role, user.login, 'MAILQUOTA_DEFAULT');
      delete $scope.non_default[role][user.login];
      return $scope.non_default[role].list.splice($scope.non_default[role].list.indexOf(user), 1);
    };
    $scope.saveApply = function() {
      wait.modal(gettext("Saving quotas ..."), 'progressbar');
      return $http.post('/api/lmn/quota/save', {
        users: $scope.toChange,
        groups: $scope.groupsToChange
      }).then(function() {
        $rootScope.$emit('updateWaiting', 'done');
        return $uibModal.open({
          templateUrl: '/lmn_quotas:resources/partial/apply.modal.html',
          controller: 'LMQuotasApplyModalController',
          backdrop: 'static'
        });
      });
    };
    return hotkeys.on($scope, function(key, event) {
      var current_tab;
      current_tab = $scope.tabs[$scope.activeTab];
      if (key === 'F' && event.ctrlKey) {
        if ($scope.activeTab <= 2) {
          $scope.showUserSearch();
          return true;
        }
        return false;
      }
      if (key === 'S' && event.ctrlKey) {
        $scope.saveApply();
        return true;
      }
      return false;
    });
  });

}).call(this);

