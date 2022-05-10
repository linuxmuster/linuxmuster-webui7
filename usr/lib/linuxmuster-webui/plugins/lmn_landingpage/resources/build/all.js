// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lmn.landingpage', ['core', 'lmn.common']);

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lmn.landingpage').config(function($routeProvider) {
    return $routeProvider.when('/view/lmn/landingpage', {
      controller: 'LMNLandingController',
      templateUrl: '/lmn_landingpage:resources/partial/index.html'
    });
  });

  angular.module('lmn.landingpage').controller('LMNLandingController', function($scope, $http, $uibModal, $location, $route, gettext, notify, pageTitle, customFields) {
    pageTitle.set(gettext('Home'));
    $scope.getData = function(user) {
      customFields.load_user_fields(user).then(function(resp) {
        return $scope.custom_fields = resp;
      });
      return $http.get(`/api/lmn/quota/${user}`).then(function(resp) {
        var ref, results, share, total, type, usage, used, values;
        $scope.quotas = [];
        $scope.user['sophomorixCloudQuotaCalculated'] = resp.data['sophomorixCloudQuotaCalculated'];
        $scope.user['sophomorixMailQuotaCalculated'] = resp.data['sophomorixMailQuotaCalculated'];
        ref = resp.data['QUOTA_USAGE_BY_SHARE'];
        results = [];
        for (share in ref) {
          values = ref[share];
          // default-school and linuxmuster-global both needed ?
          // cloudquota and mailquota not in QUOTA_USAGE_BY_SHARE ?
          used = values['USED_MiB'];
          total = values['HARD_LIMIT_MiB'];
          if (typeof total === 'string') {
            if (total === 'NO LIMIT') {
              total = gettext('NO LIMIT');
            }
            results.push($scope.quotas.push({
              'share': share,
              'total': gettext(total),
              'used': used,
              'usage': 0,
              'type': "success"
            }));
          } else {
            usage = Math.floor((100 * used) / total);
            if (usage < 60) {
              type = "success";
            } else if (usage < 80) {
              type = "warning";
            } else {
              type = "danger";
            }
            results.push($scope.quotas.push({
              'share': share,
              'total': total + " MiB",
              'used': used,
              'usage': usage,
              'type': type
            }));
          }
        }
        return results;
      });
    };
    $scope.isListAttr = function(attr_name) {
      return customFields.isListAttr(attr_name);
    };
    $scope.changePassword = function() {
      return $location.path('/view/lmn/change-password');
    };
    $scope.changeCustomFields = function() {
      return $uibModal.open({
        templateUrl: '/lmn_landingpage:resources/partial/customFields.modal.html',
        controller: 'LMNUserCustomFieldsController',
        size: 'md',
        resolve: {
          custom_fields: function() {
            return $scope.custom_fields;
          },
          user: function() {
            return $scope.user;
          }
        }
      }).closed.then(function() {
        return $route.reload();
      });
    };
    return $scope.$watch('identity.user', function() {
      var category, cn, dn, i, len, ref;
      if ($scope.identity.user === void 0) {
        return;
      }
      if ($scope.identity.user === null) {
        return;
      }
      if ($scope.identity.user === 'root') {
        return;
      }
      $scope.user = $scope.identity.profile;
      $scope.getData($scope.identity.user);
      $scope.groups = [];
      ref = $scope.user['memberOf'];
      for (i = 0, len = ref.length; i < len; i++) {
        dn = ref[i];
        cn = dn.split(',')[0].split('=')[1];
        category = dn.split(',')[1].split('=')[1];
        if (category !== "Management") {
          // User don't need to see management groups
          // User only see explicit lmn groups, no custom groups

          // Determine classes by group dn
          if (category === cn) {
            $scope.groups.push({
              'cn': cn,
              'category': gettext('Class')
            });
          }
          if (category === "Teachers") {
            $scope.groups.push({
              'cn': cn,
              'category': gettext('Teachers')
            });
          }
          if (category === "printer-groups") {
            $scope.groups.push({
              'cn': cn,
              'category': gettext('Printers')
            });
          }
          if (category === "Projects") {
            $scope.groups.push({
              'cn': cn,
              'category': gettext('Project')
            });
          }
        }
      }
    });
  });

  angular.module('lmn.users').controller('LMNUserCustomFieldsController', function($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, user, customFields, custom_fields) {
    $scope.custom_fields = custom_fields;
    $scope.user = user;
    $scope.id = user.sAMAccountName;
    $scope.isListAttr = function(attr_name) {
      return customFields.isListAttr(attr_name);
    };
    $scope.editCustom = function(custom) {
      var n, value;
      value = custom.value;
      n = custom.attr.slice(-1);
      return messagebox.prompt(gettext('New value'), value).then(function(msg) {
        return $http.post("/api/lm/custom", {
          index: n,
          value: msg.value,
          user: $scope.id
        }).then(function() {
          if (msg.value) {
            custom.value = msg.value;
          } else {
            custom.value = 'null';
          }
          return notify.success(gettext("Value updated !"));
        }, function() {
          return notify.error(gettext("Error, please verify the user and/or your values."));
        });
      });
    };
    $scope.removeCustomMulti = function(custom, value) {
      var n;
      n = custom.attr.slice(-1);
      return messagebox.show({
        title: gettext('Remove custom field value'),
        text: gettext('Do you really want to remove ') + value + ' ?',
        positive: gettext('OK'),
        negative: gettext('Cancel')
      }).then(function(msg) {
        return $http.post("/api/lm/custommulti/remove", {
          index: n,
          value: value,
          user: $scope.id
        }).then(function() {
          var position;
          position = custom.value.indexOf(value);
          custom.value.splice(position, 1);
          return notify.success(gettext("Value removed !"));
        }, function() {
          return notify.error(gettext("Error, please verify the user and/or your values."));
        });
      });
    };
    $scope.addCustomMulti = function(custom) {
      var n;
      n = custom.attr.slice(-1);
      return messagebox.prompt(gettext('New value')).then(function(msg) {
        return $http.post("/api/lm/custommulti/add", {
          index: n,
          value: msg.value,
          user: $scope.id
        }).then(function() {
          if (msg.value) {
            custom.value.push(msg.value);
            notify.success(gettext("Value added !"));
            return console.log(custom);
          }
        }, function() {
          return notify.error(gettext("Error, please verify the user and/or your values."));
        });
      });
    };
    $scope.removeProxyAddresses = function(custom, value) {
      return messagebox.show({
        title: gettext('Remove proxy address'),
        text: gettext('Do you really want to remove ') + value + ' ?',
        positive: gettext('OK'),
        negative: gettext('Cancel')
      }).then(function(msg) {
        return $http.post("/api/lm/changeProxyAddresses", {
          action: 'remove',
          address: value,
          user: $scope.id
        }).then(function() {
          var position;
          position = custom.value.indexOf(value);
          custom.value.splice(position, 1);
          return notify.success(gettext("Value removed !"));
        }, function() {
          return notify.error(gettext("Error, please verify the user and/or your values."));
        });
      });
    };
    $scope.addProxyAddresses = function(custom) {
      var n;
      n = custom.attr.slice(-1);
      return messagebox.prompt(gettext('New address')).then(function(msg) {
        return $http.post("/api/lm/changeProxyAddresses", {
          action: 'add',
          address: msg.value,
          user: $scope.id
        }).then(function() {
          if (msg.value) {
            custom.value.push(msg.value);
          }
          return notify.success(gettext("Address added !"));
        }, function() {
          return notify.error(gettext("Error, please verify the user and/or your values."));
        });
      });
    };
    return $scope.close = function() {
      return $uibModalInstance.dismiss();
    };
  });

}).call(this);

