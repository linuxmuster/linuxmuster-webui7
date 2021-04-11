'use strict';

angular.module('lmn.home', ['core', 'flow', 'lmn.samba']);


'use strict';

angular.module('lmn.home').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/home', {
        templateUrl: '/lmn_home:resources/partial/index.html',
        controller: 'HomeIndexController'
    });
});


'use strict';

angular.module('lmn.home').controller('HomeIndexController', function ($scope, $routeParams, $location, $localStorage, $timeout, notify, identity, samba, pageTitle, urlPrefix, tasks, messagebox, gettext) {
    pageTitle.set('path', $scope);

    $scope.loading = true;
    $scope.root = false;

    identity.promise.then(function () {
        if (identity.user == 'root') {
            $scope.root = true;
            $scope.loading = false;
        } else {
            $scope.home = identity.profile.homeDirectory;
            $scope.load_path($scope.home);
        }
    });

    $scope.load_path = function (path) {
        samba.list(path).then(function (data) {
            $scope.items = data.items;
            if (path == $scope.home) {
                $scope.parent = '';
            } else {
                $scope.parent = $scope.home;
            }
        }, function (data) {
            notify.error(gettext('Could not load directory'), data.message);
        }).finally(function () {
            $scope.loading = false;
        });
    };
});


