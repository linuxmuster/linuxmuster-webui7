angular.module('lmn.samba_shares').controller('HomeIndexController', function($scope, $routeParams, $window, $localStorage, $timeout, $q, $http, notify, identity, smbclient, pageTitle, urlPrefix, messagebox, gettext) {
    pageTitle.set('path', $scope);

    $scope.loading = true;
    $scope.active_share = '';

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

    $scope.delete_file = (path) => {
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

    $scope.create_dir = () => {
        messagebox.prompt(gettext('New directory name :'), '').then( (msg) => {
            path = $scope.current_path + '/' + msg.value;
            smbclient.createDirectory(path).then((data) => {
                notify.success(path + gettext(' created !'));
            $scope.reload();
        }, (resp) => {
                notify.error(gettext('Error during creating directory: '), resp.data.message);
            });
        });
    };

    $scope.delete_dir = (path) => {
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

    $scope.download = (path) => {
        $window.open(`/api/lmn/smbclient/download/${path}`);
    };

});
