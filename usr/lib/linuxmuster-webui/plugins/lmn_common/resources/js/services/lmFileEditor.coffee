angular.module('lmn.common').service 'lmFileEditor', ($uibModal) ->
    @show = (path, encoding) ->
        return $uibModal.open(
            templateUrl: '/lmn_common:resources/partial/lmFileEditor.modal.html'
            controller: 'lmFileEditorModalController'
            size: 'lg'
            resolve:
                path: () -> path
                encoding: () -> encoding
        ).result

    return this


angular.module('lmn.common').controller 'lmFileEditorModalController', ($scope, $uibModalInstance, $timeout, filesystem, path, encoding) ->
    $scope.path = path

    filesystem.read(path, encoding).then (data) ->
        $scope.content = data

    $scope.save = () ->
        filesystem.write(path, $scope.content, encoding).then () ->
            $uibModalInstance.close($scope.content)

    $scope.cancel = () ->
        $uibModalInstance.dismiss()

    $timeout () ->
        dropZone = $('.lm-file-editor-drop-target')[0]

        dropZone.addEventListener 'dragover', (e) ->
            e.stopPropagation()
            e.preventDefault()
            e.dataTransfer.dropEffect = 'copy'

        dropZone.addEventListener 'drop', (e) ->
            e.stopPropagation()
            e.preventDefault()
            files = e.dataTransfer.files
            for file in files
                do (file) ->
                    reader = new FileReader()
                    reader.onload = (e) ->
                        $scope.$apply () ->
                            $scope.content = e.target.result
                    reader.readAsText(file, encoding)

    $scope.download = () ->
        tokens = path.split('/')
        filesystem.downloadBlob($scope.content, 'text/csv', tokens[tokens.length - 1])
