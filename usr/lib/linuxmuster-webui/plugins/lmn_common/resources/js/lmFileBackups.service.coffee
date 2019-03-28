angular.module('lm.common').service 'lmFileBackups', ($uibModal) ->
    @show = (path, encoding) ->
        return $uibModal.open(
            templateUrl: '/lmn_common:resources/js/lmFileBackups.modal.html'
            controller: 'lmFileBackupsModalController'
            resolve:
                path: () -> path
                encoding: () -> encoding
        ).result

    return this


angular.module('lm.common').controller 'lmFileBackupsModalController', ($scope, $uibModalInstance, $route, $http, gettext, notify, filesystem, path, encoding, messagebox, lmFileBackups) ->
    $scope.path = path

    dir = path.substring(0, path.lastIndexOf('/'))
    name = path.substring(path.lastIndexOf('/') + 1)

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
        $http.post('/api/lm/remove-file', {filepath: backup.name}).then (resp) -> 
            pos = $scope.findIndex($scope.findbackup(backupname))
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
