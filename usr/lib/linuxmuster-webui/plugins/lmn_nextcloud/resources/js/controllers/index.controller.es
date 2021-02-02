angular.module('lmn.nextcloud').controller('LMN_nextcloudIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Nextcloud'));
    $scope.responsecode = 1;

    $scope.startNextcloud = (user) => {
        $http.get('/api/lmn/nextcloud').then( (resp) => {
            $scope.responsecode = 2;
            $scope.responsecode = resp.data[0];
            $scope.url = resp.data[1];
            $scope.fullscreen = resp.data[2];
            $scope.askuser = resp.data[3];
            console.log("Nextcloud INFO: URL = " + $scope.url + " Code = " + $scope.responsecode);
            if($scope.responsecode == 200) {
                if($scope.fullscreen) {
                    $scope.toggleNavigation();
                    $scope.toggleWidescreen();
                }
                if($scope.askuser) {
                    $scope.url += "/index.php/login?user=" + $scope.identity.user;
                }
                window.open($scope.url, 'iframe_nextcloud');
            }
        });
    }

    $scope.$watch('identity.user', function() {
        if ($scope.identity.user == undefined) { return; }
        if ($scope.identity.user == null) { return; }
        // if ($scope.identity.user == 'root') { return; }

        $scope.user = $scope.identity.profile;
        $scope.startNextcloud($scope.identity.user);
    });
});
