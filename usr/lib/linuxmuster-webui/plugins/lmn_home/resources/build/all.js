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
            $scope.current_path = $scope.home;
            $scope.load_path($scope.home);
            $scope.splitted_path = [];
        }
    });

    $scope.reload = function () {
        return $scope.load_path($scope.current_path);
    };

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
            $scope.current_path = path;
        }, function (resp) {
            notify.error(gettext('Could not load directory : '), resp.data.message);
        }).finally(function () {
            $scope.loading = false;
        });
    };

    $scope.rename = function (item) {
        old_path = item.path;
        messagebox.prompt(gettext('New name :'), item.name).then(function (msg) {
            new_path = $scope.current_path + '/' + msg.value;
            samba_share.move(old_path, new_path).then(function (data) {
                notify.success(old_path + gettext(' renamed to ') + new_path);
                $scope.reload();
            }, function (resp) {
                notify.error(gettext('Error during renaming: '), resp.data.message);
            });
        });
    };

    $scope.delete_file = function (path) {
        messagebox.show({
            text: gettext("Do you really want to delete this file?"),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(function () {
            samba_share.delete_file(path).then(function (data) {
                notify.success(path + gettext(' deleted !'));
                $scope.reload();
            }, function (resp) {
                notify.error(gettext('Error during deleting : '), resp.data.message);
            });
        });
    };

    $scope.create_dir = function () {
        messagebox.prompt(gettext('New directory name :'), '').then(function (msg) {
            path = $scope.current_path + '/' + msg.value;
            samba_share.createDirectory(path).then(function (data) {
                notify.success(path + gettext(' created !'));
                $scope.reload();
            }, function (resp) {
                notify.error(gettext('Error during creating directory: '), resp.data.message);
            });
        });
    };

    $scope.delete_dir = function (path) {
        messagebox.show({
            text: gettext("Do you really want to delete this directory? This is only possible if the directory is empty."),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(function () {
            samba_share.delete_dir(path).then(function (data) {
                notify.success(path + gettext(' deleted !'));
                $scope.reload();
            }, function (resp) {
                notify.error(gettext('Error during deleting : '), resp.data.message);
            });
        });
    };
});


