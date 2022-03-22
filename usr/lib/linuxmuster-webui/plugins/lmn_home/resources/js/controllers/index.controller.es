angular.module('lmn.home').controller('HomeIndexController', function($scope, $routeParams, $location, $localStorage, $timeout, notify, identity, samba_share, pageTitle, urlPrefix, tasks, messagebox, gettext) {
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

        samba_share.list(path).then((data) => {
                $scope.items = data.items;
                $scope.current_path = path;
            }, (resp) => {
                notify.error(gettext('Could not load directory : '), resp.data.message)
            }).finally(() => {
                $scope.loading = false
            });
    };

    $scope.delete_file = (path) => {
        messagebox.show({
            text: gettext("Do you really want to delete this file?"),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then( () => {
            samba_share.delete_file(path).then((data) => {
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
            samba_share.createDirectory(path).then((data) => {
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
            samba_share.delete_dir(path).then((data) => {
                notify.success(path + gettext(' deleted !'));
                $scope.reload();
            }, (resp) => {
                notify.error(gettext('Error during deleting : '), resp.data.message);
            });
        });
    };


});
