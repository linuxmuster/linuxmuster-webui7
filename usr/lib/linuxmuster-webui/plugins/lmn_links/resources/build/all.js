'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('lmn.links', ['core']);


'use strict';

angular.module('lmn.links').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/links', {
        templateUrl: '/lmn_links:resources/partial/index.html',
        controller: 'LMN_linksIndexController'
    });
});


'use strict';

angular.module('lmn.links').controller('LMN_linksIndexController', function ($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Links'));
    $scope.responsecode = 1;

    $scope.start = function () {
        $http.get('/api/lmn/links').then(function (resp) {
            if (resp.data.status == "success") {
                $scope.links_result = resp.data.data;
                $scope.links = [];
                for (var link in $scope.links_result) {
                    for (var permission in $scope.links_result[link].permissions) {
                        if ($scope.identity.profile.sophomorixRole == permission) {
                            $scope.links.push($scope.links_result[link]);
                        }
                    }
                }
            } else {
                $scope.links = [];
                console.log("LMN-Links [ERROR] - " + resp.data.message);
            }
        });
    };

    $scope.$watch('identity.user', function () {
        if ($scope.identity.user == undefined) {
            return;
        }
        if ($scope.identity.user == null) {
            return;
        }

        $scope.user = $scope.identity.profile;
        $scope.start();
    });
});


