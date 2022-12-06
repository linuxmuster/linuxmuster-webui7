angular.module('lmn.clients').controller('Lmn_clientsIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Lmn_clients'));

    $scope.pathToEdit = '';
    $scope.scriptContent = '';

    $http.get('/api/lmn/clients/scripts').then( (resp) => {
        $scope.custom_scripts_path = resp.data['path'];
	    $scope.custom_scripts_linux = resp.data['linux'];
        $scope.custom_scripts_windows = resp.data['windows'];
    });

    $scope.editScript = (script) => {
        $scope.scriptToEdit = script;
    };

    $scope.saveScript = (script) => {
        $http.post('/api/lmn/clients/scripts', {'path':script.path, 'content':script.content}).then(() => {
                $scope.scriptToEdit = '';
                notify.success(gettext('Script saved !'));
            }, () => notify.error(gettext('Error while saving script'))
        );
    };

    $scope.closeEditScript = () => {
        $scope.scriptToEdit = '';
    };

    $scope.loadDrives = () => {
        $http.get('/api/lmn/samba/drives').then((resp) => {
            $scope.drives = resp.data[0];
            $scope.availableDriveLetters = resp.data[1];
        });
    };

    $scope.updateAvailableLetters = (newValue, oldValue) => {
        for (l of $scope.availableDriveLetters) {
            if (l.letter == newValue) l.active = true;
            if (l.letter == oldValue) l.active = false;
        };
    };

    $scope.saveDrives = () => {
        $http.post('/api/lmn/samba/drives', {'drives': $scope.drives}).then((resp) =>
            notify.success(gettext('Saved !'))
            , (err) => notify.error(err.data.message)
        );
    };
})
.filter('driveLettersOptions', function($filter) {
    return function(value, driveLetter) {
        return value.filter((obj) => !obj.active || obj.active && obj.letter == driveLetter);
    };
});

