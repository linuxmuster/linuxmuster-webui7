angular.module('lmn.common').service 'lmFileBackups', ($uibModal) ->
    @show = (path, encoding) ->
        return $uibModal.open(
            templateUrl: '/lmn_common:resources/partial/lmFileBackups.modal.html'
            controller: 'lmFileBackupsModalController'
            resolve:
                path: () -> path
                encoding: () -> encoding
        ).result

    return this

angular.module('lmn.common').service 'lmFileBackupsDiff', ($uibModal) ->
    @show = (path, backup_diff) ->
        return $uibModal.open(
            templateUrl: '/lmn_common:resources/partial/lmFileBackupsDiff.modal.html'
            controller: 'lmFileBackupsDiffModalController'
            size: 'lg'
            resolve:
                path: () -> path
                backup_diff: () -> backup_diff
        ).result

    return this

angular.module('lmn.common').controller 'lmFileBackupsDiffModalController', ($scope, $uibModalInstance, path, backup_diff) ->
    $scope.path = path
    $scope.backup_diff = backup_diff

    $scope.cancel = () ->
        $uibModalInstance.dismiss()


angular.module('lmn.common').controller 'lmFileBackupsModalController', ($scope, $uibModalInstance, $route, $http, gettext, notify, filesystem, path, encoding, messagebox, lmFileBackups, lmFileBackupsDiff) ->
    $scope.path = path

    dir = path.substring(0, path.lastIndexOf('/'))
    name = path.substring(path.lastIndexOf('/') + 1)

    $scope.translations = {
        'Restore': gettext('Restore'),
        'Show differences': gettext('Show differences'),
    }

    $scope.loadBackupFiles = () ->
        filesystem.list(dir).then (data) ->
            $scope.backups = []
            for item in data.items
                if item.name.startsWith('.' + name + '.bak.')
                    tokens = item.name.split('.')
                    $scope.backups.push {
                        name: item.name
                        date: new Date(1000 * parseInt(tokens[tokens.length - 1]))
                    }
    
    $scope.loadBackupFiles()            

    $scope.diff = (backup) ->
        $http.post('/api/lmn/diff', {file1:path, file2: dir + '/' + backup.name}).then (resp) ->
            $scope.backup_diff = resp.data
            lmFileBackupsDiff.show($scope.path, $scope.backup_diff)

    $scope.restore = (backup) ->
        filesystem.read(dir + '/' + backup.name, encoding).then (content) ->
            filesystem.write(path, content, encoding).then () ->
                $scope.onlyremove(backup)
                notify.success('Backup file restored')
                $uibModalInstance.close()
                $route.reload()
    
    $scope.findbackup = (name) ->
        return (dict) ->
            dict.name == name
    
    $scope.onlyremove = (backup) ->
        $http.post('/api/lmn/remove-file', {filepath: dir + '/' + backup.name}).then (resp) ->
            pos = $scope.backups.findIndex($scope.findbackup(backup.name))
            delete $scope.backups[pos]

    $scope.removeUI = (backup) ->
        $uibModalInstance.close()
        content = gettext('Do you really want to delete') + backup.name + ' ?'
        messagebox.show(title: gettext('Confirmation'), text: content, positive: 'OK', negative: gettext('Cancel'))
        .then () ->
            $scope.onlyremove(backup)
            notify.success('Backup file removed')
            lmFileBackups.show($scope.path)

    $scope.cancel = () ->
        $uibModalInstance.dismiss()
