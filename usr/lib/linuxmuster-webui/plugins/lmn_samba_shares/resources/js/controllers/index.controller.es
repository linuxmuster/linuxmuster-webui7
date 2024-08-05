angular.module('lmn.samba_shares').controller('HomeIndexController', function($scope, $routeParams, $window, $localStorage, $timeout, $q, $http, notify, identity, smbclient, pageTitle, urlPrefix, messagebox, gettext, tasks, toaster) {
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
        'file': "far fa-file",
    }

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

    $scope.isProtectedFile = (item) => {
        // Actually only 2 file types, restraining tests
        if (["transfer", ".upload"].includes(item.name)) {
            return $scope.protectedFiles.indexOf(item.path) > -1;
        }
        return false;
    };

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
        $scope.protectedFiles = [];

        if (shareObj.name =='Home')
            $scope.protectedFiles.push(`${shareObj.path}/transfer`);
            $scope.protectedFiles.push(`${shareObj.path}/.upload`);

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
                toaster.pop('error', gettext("Could not load directory : "), resp.data.message, 5000);
            }).finally(() => {
                $scope.loading = false
            });
    };

    $scope.get_file_icon = (filetype) => {
        return $scope.file_icon[filetype];
    }

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

    $scope.addClipboardOperation = (item, mode) => {
        for (element of $scope.clipboard) {
            if (element.item.path == item.path) {
                position = $scope.clipboard.indexOf(element);
                $scope.clipboard.splice(position, 1);
            };
        };
        $scope.clipboard.push({item, 'mode': mode});
    };

    $scope.doCut = () => {
        for (let item of $scope.items) {
            if (item.selected) {
                $scope.addClipboardOperation(item, 'move');
            }
        }
        $scope.clear_selection();
    };

    $scope.doCopy = () => {
        for (let item of $scope.items) {
            if (item.selected) {
                $scope.addClipboardOperation(item, 'copy');
            }
        }
        $scope.clear_selection();
    };

    $scope.doPaste = () => {
        // Cut and/or copy a list of files
        // Problem with error handling in promise list
        let items = angular.copy($scope.clipboard);
        promises = []
        msgbox_promises = []
        for (let item of items) {
            destination = $scope.current_path + '/' + item.item.name
            if (item.mode == 'copy') {
                if (item.item.path == destination) {
                    question = gettext('A file/directory with this name already exists, please give a new name :');
                    msgbox_promises.push(messagebox.prompt(question, item.item.name).then( (msg) => {
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
        }
        $q.all(msgbox_promises).then(() => {
            $q.all(promises).then(() => {
                $scope.clear_selection();
                $scope.clearClipboard();
                $scope.reload();
            });
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
            for (let item of items) {
                if (item.isDir) {
                    smbclient.delete_dir(item.path).then(() => notify.success(item.name + ' deleted!')).catch(err => notify.error(err));
                } else {
                    smbclient.delete_file(item.path).then(() => notify.success(item.name + ' deleted!')).catch(err => notify.error(err));
                }
            }
            $scope.clear_selection();
            $scope.reload();
        })

    $scope.delete_dir = (path) => {
        messagebox.show({
            text: gettext("Do you really want to delete this directory?"),
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
        $scope.newFileName = '';
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

    $scope.areUploadsFinished = () => {
        numUploads = $scope.uploadProgress.length;
        if (numUploads == 0) {
            return true;
        };

        globalProgress = 0;
        for (p of $scope.uploadProgress) {
            globalProgress += p.progress;
        }
        return numUploads * 100 == globalProgress;
    }

    $scope.sambaSharesUploadBegin = ($flow) => {
        $scope.uploadProgress = [];
        $scope.uploadFiles = [];
        for (file in $flow.files) {
            $scope.uploadFiles.push(file.name);
        }
        $scope.files_list = $scope.uploadFiles.join(', ');
        smbclient.startFlowUpload($flow, $scope.current_path).then((resp) => {
            notify.success(gettext('Uploaded ') + $scope.files_list);
            $scope.reload();
        }, null, (progress) => {
            $scope.uploadProgress = progress.sort((a, b) => a.name > b.name);
        });
    };
});
