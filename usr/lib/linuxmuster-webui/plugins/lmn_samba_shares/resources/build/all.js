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

angular.module('lmn.samba_shares').controller('HomeIndexController', function ($scope, $routeParams, $window, $localStorage, $timeout, $q, $http, notify, identity, smbclient, pageTitle, urlPrefix, messagebox, gettext, tasks) {
    pageTitle.set(gettext('Samba shares'));

    $scope.loading = true;
    $scope.active_share = '';
    $scope.newDirectoryDialogVisible = false;
    $scope.newFileDialogVisible = false;
    $scope.clipboardVisible = false;

    identity.promise.then(function () {
        if (identity.user == 'root') {
            $scope.loading = false;
        } else {
            smbclient.shares(identity.user).then(function (resp) {
                $scope.shares = resp;
                var _iteratorNormalCompletion = true;
                var _didIteratorError = false;
                var _iteratorError = undefined;

                try {
                    for (var _iterator = $scope.shares[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                        share = _step.value;

                        if (share.name == 'Home') {
                            $scope.active_share = share;
                            $scope.current_path = share.path;
                            $scope.load_share(share);
                            $scope.splitted_path = [];
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
            });
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

    $scope.load_share = function (shareObj) {
        var _iteratorNormalCompletion2 = true;
        var _didIteratorError2 = false;
        var _iteratorError2 = undefined;

        try {
            for (var _iterator2 = $scope.shares[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                share = _step2.value;

                share.active = false;
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

        shareObj.active = true;
        $scope.active_share = shareObj;
        $scope.load_path(shareObj.path);
    };

    $scope.load_path = function (path) {
        $scope.splitted_path_items = path.replace($scope.active_share.path, '').split('/');
        $scope.splitted_path = [];
        progressive_path = $scope.active_share.path;
        var _iteratorNormalCompletion3 = true;
        var _didIteratorError3 = false;
        var _iteratorError3 = undefined;

        try {
            for (var _iterator3 = $scope.splitted_path_items[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
                item = _step3.value;

                if (item != '') {
                    progressive_path = progressive_path + '/' + item;
                    $scope.splitted_path.push({ 'path': progressive_path, 'name': item });
                }
            }
        } catch (err) {
            _didIteratorError3 = true;
            _iteratorError3 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion3 && _iterator3.return) {
                    _iterator3.return();
                }
            } finally {
                if (_didIteratorError3) {
                    throw _iteratorError3;
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

    $scope.doCut = function () {
        var _iteratorNormalCompletion4 = true;
        var _didIteratorError4 = false;
        var _iteratorError4 = undefined;

        try {
            for (var _iterator4 = $scope.items[Symbol.iterator](), _step4; !(_iteratorNormalCompletion4 = (_step4 = _iterator4.next()).done); _iteratorNormalCompletion4 = true) {
                var _item = _step4.value;

                if (_item.selected) {
                    $scope.clipboard.push({
                        mode: 'move',
                        item: _item
                    });
                }
            }
        } catch (err) {
            _didIteratorError4 = true;
            _iteratorError4 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion4 && _iterator4.return) {
                    _iterator4.return();
                }
            } finally {
                if (_didIteratorError4) {
                    throw _iteratorError4;
                }
            }
        }

        $scope.clear_selection();
    };

    $scope.doCopy = function () {
        var _iteratorNormalCompletion5 = true;
        var _didIteratorError5 = false;
        var _iteratorError5 = undefined;

        try {
            for (var _iterator5 = $scope.items[Symbol.iterator](), _step5; !(_iteratorNormalCompletion5 = (_step5 = _iterator5.next()).done); _iteratorNormalCompletion5 = true) {
                var _item2 = _step5.value;

                if (_item2.selected) {
                    $scope.clipboard.push({
                        mode: 'copy',
                        item: _item2
                    });
                }
            }
        } catch (err) {
            _didIteratorError5 = true;
            _iteratorError5 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion5 && _iterator5.return) {
                    _iterator5.return();
                }
            } finally {
                if (_didIteratorError5) {
                    throw _iteratorError5;
                }
            }
        }

        $scope.clear_selection();
    };

    $scope.doPaste = function () {
        var items = angular.copy($scope.clipboard);
        console.log(items);
        promises = [];
        var _iteratorNormalCompletion6 = true;
        var _didIteratorError6 = false;
        var _iteratorError6 = undefined;

        try {
            for (var _iterator6 = items[Symbol.iterator](), _step6; !(_iteratorNormalCompletion6 = (_step6 = _iterator6.next()).done); _iteratorNormalCompletion6 = true) {
                var _item3 = _step6.value;

                if (_item3.mode == 'copy') {
                    promises.push(smbclient.copy(_item3.item.path, $scope.current_path + '/' + _item3.item.name));
                }
                if (_item3.mode == 'move') {
                    promises.push(smbclient.move(_item3.item.path, $scope.current_path + '/' + _item3.item.name));
                }
            }
        } catch (err) {
            _didIteratorError6 = true;
            _iteratorError6 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion6 && _iterator6.return) {
                    _iterator6.return();
                }
            } finally {
                if (_didIteratorError6) {
                    throw _iteratorError6;
                }
            }
        }

        $q.all(promises).then(function () {
            notify.success('Done !');
            $scope.clear_selection();
            $scope.clearClipboard();
            $scope.reload();
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
            var _iteratorNormalCompletion7 = true;
            var _didIteratorError7 = false;
            var _iteratorError7 = undefined;

            try {
                for (var _iterator7 = items[Symbol.iterator](), _step7; !(_iteratorNormalCompletion7 = (_step7 = _iterator7.next()).done); _iteratorNormalCompletion7 = true) {
                    var _item4 = _step7.value;

                    promises.push(smbclient.delete_file(_item4.path));
                }
            } catch (err) {
                _didIteratorError7 = true;
                _iteratorError7 = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion7 && _iterator7.return) {
                        _iterator7.return();
                    }
                } finally {
                    if (_didIteratorError7) {
                        throw _iteratorError7;
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

    $localStorage.sambaSharesClipboard = $localStorage.sambaSharesClipboard || [];
    $scope.clipboard = $localStorage.sambaSharesClipboard;

    $scope.showClipboard = function () {
        return $scope.clipboardVisible = true;
    };

    $scope.hideClipboard = function () {
        return $scope.clipboardVisible = false;
    };

    $scope.clearClipboard = function () {
        $scope.clipboard.length = 0;
        $scope.hideClipboard();
    };

    // new file dialog

    $scope.showNewFileDialog = function () {
        $scope.newFileName = '';console.log("test");
        $scope.newFileDialogVisible = true;
    };

    $scope.doCreateFile = function () {
        if (!$scope.newFileName) {
            return;
        }
        return smbclient.createFile($scope.current_path + '/' + $scope.newFileName).then(function () {
            $scope.reload();
            $scope.newFileDialogVisible = false;
        }, function (err) {
            notify.error(gettext('Could not create file'), err.data.message);
        });
    };

    // new directory dialog

    $scope.showNewDirectoryDialog = function () {
        $scope.newDirectoryName = '';
        $scope.newDirectoryDialogVisible = true;
    };

    $scope.doCreateDirectory = function () {
        if (!$scope.newDirectoryName) {
            return;
        }

        return smbclient.createDirectory($scope.current_path + '/' + $scope.newDirectoryName).then(function () {
            $scope.reload();
            $scope.newDirectoryDialogVisible = false;
        }, function (err) {
            notify.error(gettext('Could not create directory'), err.data.message);
        });
    };

    $scope.download = function (path) {
        $http.head('/api/lmn/smbclient/download?path=' + path).then(function (resp) {
            $window.open('/api/lmn/smbclient/download?path=' + path);
        }, function (resp) {
            notify.error(gettext('File not found, may be due to special chars in the file name.'));
        });
    };
});


