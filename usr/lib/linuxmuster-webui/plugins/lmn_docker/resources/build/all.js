'use strict';

angular.module('lmn.docker', ['core']);


'use strict';

angular.module('lmn.docker').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn/docker', {
        templateUrl: '/lmn_docker:resources/partial/index.html',
        controller: 'DockerLMNIndexController'
    });
});


'use strict';

angular.module('lmn.docker').controller('DockerLMNIndexController', function ($scope, $http, $interval, messagebox, pageTitle, gettext, notify) {
    pageTitle.set('Docker');
    $scope.container_stats = [];
    $scope.images = [];
    $scope.ready = false;
    $scope.imagesReady = false;

    $http.get('/api/lmn/docker/which').then(function () {
        $scope.getResources();
        $scope.start_refresh();
        $scope.installed = true;
    }, function (err) {
        $scope.ready = true;
        $scope.installed = false;
    });

    $scope.start_refresh = function () {
        if ($scope.refresh === undefined) $scope.refresh = $interval($scope.getResources, 5000, 0);
    };
    $scope.getResources = function () {
        $http.get('/api/lmn/docker/containers', { ignoreLoadingBar: true }).then(function (resp) {
            $scope.ready = true;
            $scope.container_stats = resp.data;
        });
    };

    $scope.getDetails = function (container_id) {
        $http.get('/api/lmn/docker/container/' + container_id).then(function (resp) {
            $scope.details = resp.data;
            $scope.showDetails = true;
        });
    };

    $scope.closeDetails = function () {
        return $scope.showDetails = false;
    };

    $scope.stop = function (container_id) {
        $http.post('/api/lmn/docker/container_command', { container_id: container_id, control: 'stop' }).then(function () {
            return notify.success(gettext('Stop command successfully sent.'));
        });
    };

    $scope.start = function (container_id) {
        $http.post('/api/lmn/docker/container_command', { container_id: container_id, control: 'start' }).then(function () {
            return notify.success(gettext('Start command successfully sent.'));
        });
    };

    $scope.remove = function (container_id) {
        messagebox.show({
            text: gettext('Really remove this container?'),
            positive: gettext('Remove'),
            negative: gettext('Cancel')
        }).then(function () {
            $http.post('/api/lmn/docker/container_command', { container_id: container_id, control: 'rm' }).then(function () {
                return notify.success(gettext('Remove command successfully sent.'));
            });
        });
    };

    $scope.getImages = function () {
        $interval.cancel($scope.refresh);
        delete $scope.refresh;
        $http.get('/api/lmn/docker/images').then(function (resp) {
            $scope.images = resp.data;console.log($scope.images);
            $scope.imagesReady = true;
        });
    };

    $scope.removeImage = function (image_id) {
        messagebox.show({
            text: gettext('Really remove this image?'),
            positive: gettext('Remove'),
            negative: gettext('Cancel')
        }).then(function () {
            $http.delete('/api/lmn/docker/image/' + image_id).then(function () {
                notify.success(gettext('Remove command successfully sent.'));
                for (var i = 0; i < $scope.images.length; i++) {
                    if ($scope.images[i].hash == image_id) $scope.images.splice(i, 1);
                }
            }, function (err) {
                return notify.error(err.data.message);
            });
        });
    };

    $scope.$on('$destroy', function () {
        return $interval.cancel($scope.refresh);
    });
});


