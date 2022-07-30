angular.module('lmn.clients').controller('Lmn_clientsIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Lmn_clients'));

    $scope.pathToEdit = '';
    $scope.scriptContent = '';

    $http.get('/api/lmn_clients_scripts').then( (resp) => {
        $scope.custom_scripts_path = resp.data['path'];
	    $scope.custom_scripts_linux = resp.data['linux'];
        $scope.custom_scripts_windows = resp.data['windows'];
    });

    $scope.edit = (script) => {
        $scope.scriptToEdit = script;
    };

    $scope.save = (script) => {
        $http.post('/api/lmn_client_script', {'path':script.path, 'content':script.content}).then(() => {
                $scope.scriptToEdit = '';
                notify.success(gettext('Script saved !'));
            }, () => notify.error(gettext('Error while saving script'))
        );
    };

    $scope.close = () => {
        $scope.scriptToEdit = '';
    };
});

