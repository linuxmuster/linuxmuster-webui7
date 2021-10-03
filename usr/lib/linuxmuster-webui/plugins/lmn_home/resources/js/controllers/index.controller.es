angular.module('lmn.home').controller('HomeIndexController', function($scope, $routeParams, $location, $localStorage, $timeout, notify, identity, samba_share, pageTitle, urlPrefix, tasks, messagebox, gettext) {
    pageTitle.set('path', $scope);

    $scope.loading = true;
    $scope.root = false;

    identity.promise.then(() => {
        if (identity.user == 'root') {
            $scope.root = true;
            $scope.loading = false;
        }
        else {
            $scope.home = identity.profile.homeDirectory;
            $scope.load_path($scope.home);
        }
    });

    $scope.load_path = (path) => {
        samba_share.list(path).then((data) => {
                $scope.items = data.items;
                if (path == $scope.home) {
                    $scope.parent = '';
                }
                else {
                    $scope.parent = $scope.home;
                }
            }, (data) => {
                notify.error(gettext('Could not load directory'), data.message)
            }).finally(() => {
                $scope.loading = false
            });
    };


});
