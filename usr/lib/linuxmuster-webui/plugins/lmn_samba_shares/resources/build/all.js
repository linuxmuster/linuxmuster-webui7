'use strict';

angular.module('lmn.samba_shares', ['core', 'flow', 'lmn.smbclient']);


'use strict';

angular.module('lmn.samba_shares').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/home', {
        templateUrl: '/lmn_samba_shares:resources/partial/index.html',
        controller: 'HomeIndexController'
    });
});


'use strict';

angular.module('lmn.samba_shares').controller('HomeIndexController', function ($scope, $routeParams, $window, $localStorage, $timeout, $q, $http, notify, identity, smbclient, pageTitle, urlPrefix, messagebox, gettext) {
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

    $scope.clear_selection = function () {
        $scope.items.forEach(function (item) {
            return item.selected = false;
        });
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

        smbclient.list(path).then(function (data) {
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
            smbclient.move(old_path, new_path).then(function (data) {
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
            smbclient.delete_file(path).then(function (data) {
                notify.success(path + gettext(' deleted !'));
                $scope.reload();
            }, function (resp) {
                notify.error(gettext('Error during deleting : '), resp.data.message);
            });
        });
    };

    $scope.doDelete = function () {
        return messagebox.show({
            text: gettext('Delete selected items?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(function () {
            var items = $scope.items.filter(function (item) {
                return item.selected;
            });
            promises = [];
            var _iteratorNormalCompletion2 = true;
            var _didIteratorError2 = false;
            var _iteratorError2 = undefined;

            try {
                for (var _iterator2 = items[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                    var _item = _step2.value;

                    promises.push(smbclient.delete_file(_item.path));
                }
            } catch (err) {
                _didIteratorError2 = true;
                _iteratorError2 = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion2 && _iterator2.return) {
                        _iterator2.return();
                    }
                } finally {
                    if (_didIteratorError2) {
                        throw _iteratorError2;
                    }
                }
            }

            $q.all(promises).then(function () {
                notify.success('Deleted !');
                $scope.clear_selection();
                $scope.reload();
            });
        });
    };

    $scope.create_dir = function () {
        messagebox.prompt(gettext('New directory name :'), '').then(function (msg) {
            path = $scope.current_path + '/' + msg.value;
            smbclient.createDirectory(path).then(function (data) {
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
            smbclient.delete_dir(path).then(function (data) {
                notify.success(path + gettext(' deleted !'));
                $scope.reload();
            }, function (resp) {
                notify.error(gettext('Error during deleting : '), resp.data.message);
            });
        });
    };

    $scope.download = function (path) {
        $window.open('/api/lmn/smbclient/download/' + path);
    };
});


