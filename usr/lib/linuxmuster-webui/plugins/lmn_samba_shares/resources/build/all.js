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

angular.module('lmn.samba_shares').controller('HomeIndexController', function ($scope, $routeParams, $window, $localStorage, $timeout, $q, $http, notify, identity, smbclient, pageTitle, urlPrefix, messagebox, gettext, tasks, toaster) {
    pageTitle.set(gettext('Samba shares'));

    $scope.loading = true;
    $scope.active_share = '';
    $scope.newDirectoryDialogVisible = false;
    $scope.newFileDialogVisible = false;
    $scope.clipboardVisible = false;
    $scope.uploadProgress = [];
    $scope.file_icon = {
        'powerpoint': "far fa-file-powerpoint",
        'text': "far fa-file-alt",
        'code': "far fa-file-code",
        'word': "far fa-file-word",
        'pdf': "far fa-file-pdf",
        'excel': "far fa-file-excel",
        'audio': "far fa-file-audio",
        'archive': "far fa-file-archive",
        'video': "far fa-file-video",
        'image': "far fa-file-image",
        'file': "far fa-file"
    };

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

    $scope.isProtectedFile = function (item) {
        // Actually only 2 file types, restraining tests
        if (["transfer", ".upload"].includes(item.name)) {
            return $scope.protectedFiles.indexOf(item.path) > -1;
        }
        return false;
    };

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
        $scope.protectedFiles = [];

        if (shareObj.name == 'Home') $scope.protectedFiles.push(shareObj.path + '/transfer');
        $scope.protectedFiles.push(shareObj.path + '/.upload');

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
            toaster.pop('error', gettext("Could not load directory : "), resp.data.message, 5000);
        }).finally(function () {
            $scope.loading = false;
        });
    };

    $scope.get_file_icon = function (filetype) {
        return $scope.file_icon[filetype];
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

    $scope.addClipboardOperation = function (item, mode) {
        var _iteratorNormalCompletion4 = true;
        var _didIteratorError4 = false;
        var _iteratorError4 = undefined;

        try {
            for (var _iterator4 = $scope.clipboard[Symbol.iterator](), _step4; !(_iteratorNormalCompletion4 = (_step4 = _iterator4.next()).done); _iteratorNormalCompletion4 = true) {
                element = _step4.value;

                if (element.item.path == item.path) {
                    position = $scope.clipboard.indexOf(element);
                    $scope.clipboard.splice(position, 1);
                };
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

        ;
        $scope.clipboard.push({ item: item, 'mode': mode });
    };

    $scope.doCut = function () {
        var _iteratorNormalCompletion5 = true;
        var _didIteratorError5 = false;
        var _iteratorError5 = undefined;

        try {
            for (var _iterator5 = $scope.items[Symbol.iterator](), _step5; !(_iteratorNormalCompletion5 = (_step5 = _iterator5.next()).done); _iteratorNormalCompletion5 = true) {
                var _item = _step5.value;

                if (_item.selected) {
                    $scope.addClipboardOperation(_item, 'move');
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

    $scope.doCopy = function () {
        var _iteratorNormalCompletion6 = true;
        var _didIteratorError6 = false;
        var _iteratorError6 = undefined;

        try {
            for (var _iterator6 = $scope.items[Symbol.iterator](), _step6; !(_iteratorNormalCompletion6 = (_step6 = _iterator6.next()).done); _iteratorNormalCompletion6 = true) {
                var _item2 = _step6.value;

                if (_item2.selected) {
                    $scope.addClipboardOperation(_item2, 'copy');
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

        $scope.clear_selection();
    };

    $scope.doPaste = function () {
        // Cut and/or copy a list of files
        // Problem with error handling in promise list
        var items = angular.copy($scope.clipboard);
        promises = [];
        msgbox_promises = [];
        var _iteratorNormalCompletion7 = true;
        var _didIteratorError7 = false;
        var _iteratorError7 = undefined;

        try {
            var _loop = function _loop() {
                var item = _step7.value;

                destination = $scope.current_path + '/' + item.item.name;
                if (item.mode == 'copy') {
                    if (item.item.path == destination) {
                        question = gettext('A file/directory with this name already exists, please give a new name :');
                        msgbox_promises.push(messagebox.prompt(question, item.item.name).then(function (msg) {
                            new_destination = $scope.current_path + '/' + msg.value;
                            promises.push(smbclient.copy(item.item.path, new_destination));
                        }));
                    } else {
                        if (item.item.path != destination) {
                            promises.push(smbclient.copy(item.item.path, destination));
                        }
                    }
                }
                if (item.mode == 'move') {
                    promises.push(smbclient.move(item.item.path, $scope.current_path + '/' + item.item.name));
                }
            };

            for (var _iterator7 = items[Symbol.iterator](), _step7; !(_iteratorNormalCompletion7 = (_step7 = _iterator7.next()).done); _iteratorNormalCompletion7 = true) {
                _loop();
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

        $q.all(msgbox_promises).then(function () {
            $q.all(promises).then(function () {
                $scope.clear_selection();
                $scope.clearClipboard();
                $scope.reload();
            });
        });
    };

    $scope.delete_file = function (path) {
        // Delete directly one single file
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
        return (
            // Delete a list of selected files
            // Problem with error handling in promise list
            messagebox.show({
                text: gettext('Delete selected items?'),
                positive: gettext('Delete'),
                negative: gettext('Cancel')
            }).then(function () {
                var items = $scope.items.filter(function (item) {
                    return item.selected;
                });
                promises = [];
                var _iteratorNormalCompletion8 = true;
                var _didIteratorError8 = false;
                var _iteratorError8 = undefined;

                try {
                    for (var _iterator8 = items[Symbol.iterator](), _step8; !(_iteratorNormalCompletion8 = (_step8 = _iterator8.next()).done); _iteratorNormalCompletion8 = true) {
                        var _item3 = _step8.value;

                        if (_item3.isDir) {
                            promises.push(smbclient.delete_dir(_item3.path));
                        } else {
                            promises.push(smbclient.delete_file(_item3.path));
                        }
                    }
                } catch (err) {
                    _didIteratorError8 = true;
                    _iteratorError8 = err;
                } finally {
                    try {
                        if (!_iteratorNormalCompletion8 && _iterator8.return) {
                            _iterator8.return();
                        }
                    } finally {
                        if (_didIteratorError8) {
                            throw _iteratorError8;
                        }
                    }
                }

                $q.all(promises).then(function () {
                    notify.success('Deleted !');
                    $scope.clear_selection();
                    $scope.reload();
                }).catch(function (err) {
                    return notify.error(err);
                });
            })
        );
    };

    $scope.delete_dir = function (path) {
        messagebox.show({
            text: gettext("Do you really want to delete this directory?"),
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
        $scope.newFileName = '';
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

    $scope.areUploadsFinished = function () {
        numUploads = $scope.uploadProgress.length;
        if (numUploads == 0) {
            return true;
        };

        globalProgress = 0;
        var _iteratorNormalCompletion9 = true;
        var _didIteratorError9 = false;
        var _iteratorError9 = undefined;

        try {
            for (var _iterator9 = $scope.uploadProgress[Symbol.iterator](), _step9; !(_iteratorNormalCompletion9 = (_step9 = _iterator9.next()).done); _iteratorNormalCompletion9 = true) {
                p = _step9.value;

                globalProgress += p.progress;
            }
        } catch (err) {
            _didIteratorError9 = true;
            _iteratorError9 = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion9 && _iterator9.return) {
                    _iterator9.return();
                }
            } finally {
                if (_didIteratorError9) {
                    throw _iteratorError9;
                }
            }
        }

        return numUploads * 100 == globalProgress;
    };

    $scope.sambaSharesUploadBegin = function ($flow) {
        $scope.uploadProgress = [];
        $scope.uploadFiles = [];
        for (file in $flow.files) {
            $scope.uploadFiles.push(file.name);
        }
        $scope.files_list = $scope.uploadFiles.join(', ');
        smbclient.startFlowUpload($flow, $scope.current_path).then(function (resp) {
            notify.success(gettext('Uploaded ') + $scope.files_list);
            $scope.reload();
        }, null, function (progress) {
            $scope.uploadProgress = progress.sort(function (a, b) {
                return a.name > b.name;
            });
        });
    };
});


