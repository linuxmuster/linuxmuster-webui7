angular.module('lmn.samba_shares').controller('HomeIndexController', function($scope, $routeParams, $location, $localStorage, $timeout, notify, identity, smbclient, pageTitle, urlPrefix, tasks, messagebox, gettext) {
    pageTitle.set('path', $scope);

    $scope.loading = true;

    identity.promise.then(() => {
        if (identity.user == 'root') {
            $scope.loading = false;
        }
        else {
            $scope.home = identity.profile.homeDirectory;
            $scope.current_path = $scope.home;
            $scope.load_path($scope.home);
            $scope.splitted_path = [];
        }
    });

    $scope.reload = () =>
        $scope.load_path($scope.current_path)

    $scope.load_path = (path) => {
        $scope.splitted_path_items = path.replace($scope.home, '').split('/');
        $scope.splitted_path = [];
        progressive_path = $scope.home;
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


});
