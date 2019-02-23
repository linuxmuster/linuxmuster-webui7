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


angular.module('lm.common').controller 'lmFileBackupsModalController', ($scope, $uibModalInstance, $route, filesystem, path, encoding) ->
    $scope.path = path

    dir = path.substring(0, path.lastIndexOf('/'))
    name = path.substring(path.lastIndexOf('/') + 1)

    filesystem.list(dir).then (data) ->
        $scope.backups = []
        for item in data.items
            if item.name.startsWith('.' + name + '.bak.')
                tokens = item.name.split('.')
                $scope.backups.push {
                    name: item.name
                    date: new Date(1000 * parseInt(tokens[tokens.length - 1]))
                }

    $scope.restore = (backup) ->
        filesystem.read(dir + '/' + backup.name, encoding).then (content) ->
            filesystem.write(path, content, encoding).then () ->
                $uibModalInstance.close()
                $route.reload()

    $scope.cancel = () ->
        $uibModalInstance.dismiss()
