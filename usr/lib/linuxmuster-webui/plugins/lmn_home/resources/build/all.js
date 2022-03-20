'use strict';

angular.module('lmn.home', ['core', 'flow', 'lmn.samba_share']);


'use strict';

angular.module('lmn.home').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/home', {
        templateUrl: '/lmn_home:resources/partial/index.html',
        controller: 'HomeIndexController'
    });
});


'use strict';

angular.module('lmn.home').controller('HomeIndexController', function ($scope, $routeParams, $location, $localStorage, $timeout, notify, identity, samba_share, pageTitle, urlPrefix, tasks, messagebox, gettext) {
    pageTitle.set('path', $scope);

    $scope.loading = true;

    identity.promise.then(function () {
        if (identity.user == 'root') {
            $scope.loading = false;
        } else {
            $scope.home = identity.profile.homeDirectory;
            $scope.load_path($scope.home);
            $scope.splitted_path = [];
        }
    });

    $scope.load_path = function (path) {
        $scope.splitted_path_items = path.replace($scope.home, '').split('/');
        $scope.splitted_path = [];
        progressive_path = $scope.home;
        var _iteratorNormalCompletion = true;
        var _didIteratorError = false;
        var _iteratorError = undefined;

        try {
            for (var _iterator = $scope.splitted_path_items[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                item = _step.value;

                if (item != '') {
                    progressive_path = progressive_path + '/' + item;
                    $scope.splitted_path.push({ 'path': progressive_path, 'name': item });
                }
            }
        } catch (err) {
            _didIteratorError = true;
            _iteratorError = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion && _iterator.return) {
                    _iterator.return();
                }
            } finally {
                if (_didIteratorError) {
                    throw _iteratorError;
                }
            }
        }

        samba_share.list(path).then(function (data) {
            $scope.items = data.items;
        }, function (data) {
            notify.error(gettext('Could not load directory'), data.message);
        }).finally(function () {
            $scope.loading = false;
        });
    };
});


