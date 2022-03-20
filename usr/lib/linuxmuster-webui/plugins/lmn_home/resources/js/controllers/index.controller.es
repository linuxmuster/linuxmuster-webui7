angular.module('lmn.home').controller('HomeIndexController', function($scope, $routeParams, $location, $localStorage, $timeout, notify, identity, samba_share, pageTitle, urlPrefix, tasks, messagebox, gettext) {
    pageTitle.set('path', $scope);

    $scope.loading = true;

    identity.promise.then(() => {
        if (identity.user == 'root') {
            $scope.loading = false;
        }
        else {
            $scope.home = identity.profile.homeDirectory;
            $scope.load_path($scope.home);
            $scope.splitted_path = [];
        }
    });

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
            }, (data) => {
                notify.error(gettext('Could not load directory'), data.message)
            }).finally(() => {
                $scope.loading = false
            });
    };


});
