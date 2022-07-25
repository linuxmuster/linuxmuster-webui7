angular.module('lmn.samba_shares').controller('HomeIndexController', function($scope, $routeParams, $window, $localStorage, $timeout, $q, $http, notify, identity, smbclient, pageTitle, urlPrefix, messagebox, gettext, tasks) {
    pageTitle.set(gettext('Samba shares'));

    $scope.loading = true;
    $scope.active_share = '';
    $scope.newDirectoryDialogVisible = false;
    $scope.newFileDialogVisible = false;
    $scope.clipboardVisible = false;

    identity.promise.then(() => {
        if (identity.user == 'root') {
            $scope.loading = false;
        }
        else {
            smbclient.shares(identity.user).then((resp) => {
                $scope.shares = resp;
                for (share of $scope.shares) {
                    if (share.name == 'Home') {
                        $scope.active_share = share;
                        $scope.current_path = share.path;
                        $scope.load_share(share);
                        $scope.splitted_path = [];
                    }
                }
            });
        }
    });

    $scope.reload = () =>
        $scope.load_path($scope.current_path)

    $scope.clear_selection = () => {
        $scope.items.forEach((item) => item.selected = false)
    };

    $scope.load_share = (shareObj) => {
        for (share of $scope.shares) {
            share.active = false;
        }
        shareObj.active = true;
        $scope.active_share = shareObj;
        $scope.load_path(shareObj.path);
    }

    $scope.load_path = (path) => {
        $scope.splitted_path_items = path.replace($scope.active_share.path, '').split('/');
        $scope.splitted_path = [];
        progressive_path = $scope.active_share.path;
        for (item of $scope.splitted_path_items) {
            if (item != '') {
                progressive_path = progressive_path + '/' + item;
                $scope.splitted_path.push({'path': progressive_path, 'name': item});
            }
        }

        smbclient.list(path).then((data) => {
                $scope.items = data.items;
                $scope.current_path = path;
            }, (resp) => {
                notify.error(gettext('Could not load directory : '), resp.data.message)
            }).finally(() => {
                $scope.loading = false
            });
    };

    $scope.rename = (item) => {
        old_path = item.path;
        messagebox.prompt(gettext('New name :'), item.name).then( (msg) => {
            new_path = $scope.current_path + '/' + msg.value;
            smbclient.move(old_path, new_path).then((data) => {
                notify.success(old_path + gettext(' renamed to ') + new_path);
            $scope.reload();
        }, (resp) => {
                notify.error(gettext('Error during renaming: '), resp.data.message);
            });
        });
    };

    $scope.doCut = function() {
        for (let item of $scope.items) {
            if (item.selected) {
                $scope.clipboard.push({
                    mode: 'move',
                    item
                });
            }
        }
        $scope.clear_selection();
    };

    $scope.doCopy = function() {
        for (let item of $scope.items) {
            if (item.selected) {
                $scope.clipboard.push({
                    mode: 'copy',
                    item
                });
            }
        }
        $scope.clear_selection();
    };

    $scope.doPaste = function() {
        // Cut and/or copy a list of files
        // Problem with error handling in promise list
        let items = angular.copy($scope.clipboard);
        console.log(items);
        promises = []
        for (let item of items) {
            if (item.mode == 'copy') {
                promises.push(smbclient.copy(item.item.path, $scope.current_path + '/' + item.item.name));
            }
            if (item.mode == 'move') {
                promises.push(smbclient.move(item.item.path, $scope.current_path + '/' + item.item.name));
            }
        }
        $q.all(promises).then(() => {
            notify.success('Done !');
            $scope.clear_selection();
            $scope.clearClipboard();
            $scope.reload();
        });
    };

    $scope.delete_file = (path) => {
        // Delete directly one single file
        messagebox.show({
            text: gettext("Do you really want to delete this file?"),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then( () => {
            smbclient.delete_file(path).then((data) => {
                notify.success(path + gettext(' deleted !'));
                $scope.reload();
            }, (resp) => {
                notify.error(gettext('Error during deleting : '), resp.data.message);
            });
        });
    };

    $scope.doDelete = () =>
        // Delete a list of selected files
        // Problem with error handling in promise list
        messagebox.show({
            text: gettext('Delete selected items?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => {
            let items = $scope.items.filter((item) => item.selected);
            promises = []
            for (let item of items) {
                promises.push(smbclient.delete_file(item.path));
            }
            $q.all(promises).then(() => {
                notify.success('Deleted !');
                $scope.clear_selection();
                $scope.reload();
            });
        })

    $scope.delete_dir = (path) => {
        // Directly delete a single directory
        messagebox.show({
            text: gettext("Do you really want to delete this directory? This is only possible if the directory is empty."),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then( () => {
            smbclient.delete_dir(path).then((data) => {
                notify.success(path + gettext(' deleted !'));
                $scope.reload();
            }, (resp) => {
                notify.error(gettext('Error during deleting : '), resp.data.message);
            });
        });
    };

    $localStorage.sambaSharesClipboard = $localStorage.sambaSharesClipboard || [];
    $scope.clipboard = $localStorage.sambaSharesClipboard;

    $scope.showClipboard = () => $scope.clipboardVisible = true;

    $scope.hideClipboard = () => $scope.clipboardVisible = false;

    $scope.clearClipboard = function() {
        $scope.clipboard.length = 0;
        $scope.hideClipboard();
    };

    // new file dialog

    $scope.showNewFileDialog = function() {
        $scope.newFileName = '';console.log("test");
        $scope.newFileDialogVisible = true;
    };

    $scope.doCreateFile = function() {
        if (!$scope.newFileName) {
            return;
        }
        return smbclient.createFile($scope.current_path + '/' + $scope.newFileName).then(() => {
            $scope.reload();
            $scope.newFileDialogVisible = false;
        }, (err) => {
            notify.error(gettext('Could not create file'), err.data.message)
        });
    };

    // new directory dialog

    $scope.showNewDirectoryDialog = function() {
        $scope.newDirectoryName = '';
        $scope.newDirectoryDialogVisible = true;
    };

    $scope.doCreateDirectory = function() {
        if (!$scope.newDirectoryName) {
            return;
        }

        return smbclient.createDirectory($scope.current_path + '/' + $scope.newDirectoryName).then(() => {
            $scope.reload();
            $scope.newDirectoryDialogVisible = false;
        }, (err) => {
            notify.error(gettext('Could not create directory'), err.data.message)
        });
    };

    $scope.download = (path) => {
        $http.head(`/api/lmn/smbclient/download?path=${path}`).then((resp) => {
            $window.open(`/api/lmn/smbclient/download?path=${path}`);
        }, (resp) => {
            notify.error(gettext('File not found, may be due to special chars in the file name.'));
        });
    };

});
