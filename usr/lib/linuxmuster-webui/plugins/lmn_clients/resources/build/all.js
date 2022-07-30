'use strict';

angular.module('lmn.clients', ['lmn.common']);


'use strict';

angular.module('lmn.clients').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn_clients', {
        templateUrl: '/lmn_clients:resources/partial/index.html',
        controller: 'Lmn_clientsIndexController'
    });
});


'use strict';

angular.module('lmn.clients').controller('Lmn_clientsIndexController', function ($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Lmn_clients'));

    $scope.pathToEdit = '';
    $scope.scriptContent = '';

    $http.get('/api/lmn_clients_scripts').then(function (resp) {
        $scope.custom_scripts_path = resp.data['path'];
        $scope.custom_scripts_linux = resp.data['linux'];
        $scope.custom_scripts_windows = resp.data['windows'];
    });

    $scope.edit = function (script) {
        $scope.scriptToEdit = script;
    };

    $scope.save = function (script) {
        $http.post('/api/lmn_client_script', { 'path': script.path, 'content': script.content }).then(function () {
            $scope.scriptToEdit = '';
            notify.success(gettext('Script saved !'));
        }, function () {
            return notify.error(gettext('Error while saving script'));
        });
    };

    $scope.close = function () {
        $scope.scriptToEdit = '';
    };
});


