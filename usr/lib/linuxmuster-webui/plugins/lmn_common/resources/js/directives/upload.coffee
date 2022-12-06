angular.module('lmn.common').directive 'lmDragUpload', ($http, notify, messagebox, filesystem, gettext) ->
    return {
        restrict: 'E'
        scope: {
            uploadpath: '='
            refresh: '='
            subdir: '=?'
            movetohome: '=?'
            owner: '=?'
            group: '=?'
        }
        replace: true
        template: (attrs) ->
            if (!attrs.target)
                target = "'/api/filesystem/upload'"
            else
                target = attrs.target
            return "<div>
                        <div    flow-init=\"{target: #{target}, chunkSize: 1024 * 1024, singleFile: true}\"
                                flow-files-submitted=\"onUploadBegin($flow)\"
                                flow-drag-enter=\"class='dragdroparea-enter'\"
                                flow-drag-leave=\"class='dragdroparea'\"
                                ng-style=\"style\">
                            <div class=\"dragdroparea\" flow-drop  ng-class=\"class\">
                                <span class=\"btn btn-default\" flow-btn translate>Upload file</span>
                                <span translate> or drag And Drop your file here</span>
                            </div>

                        </div>
                    </div>"

        link: ($scope, attrs) ->
            $scope.onUploadBegin = ($flow) ->
                msg = messagebox.show({progress: true})
                filesystem.startFlowUpload($flow, $scope.uploadpath)
                .then () ->
                    if ($scope.owner and $scope.group)
                        filename=$flow.files[0].name
                        filepath=$scope.uploadpath+filename
                        $http.post('/api/lmn/chown', {filepath: $scope.uploadpath + $flow.files[0].name, owner: $scope.owner, group: $scope.group}).then () ->
                            if ($scope.movetohome)
                                $http.post('/api/lmn/session/moveFileToHome', {user: $scope.owner, filepath: $scope.uploadpath, subdir: $scope.subdir}).then (resp) ->
                                    console.log ('return')
                                    console.log (resp.data)
                                    $http.post('/api/lmn/remove-file', {filepath: filepath}).then () ->
                                        notify.success(gettext('Uploaded'))
                                        $scope.refresh()
                    else
                        notify.success(gettext('Uploaded'))
                    $scope.refresh()
                    msg.close()
                , null, (progress) ->
                    msg.messagebox.title = 'Uploading: ' + Math.floor(100 * progress) + ' %'
    }

angular.module('lmn.common').directive 'lmSelectUpload', ($http, notify, messagebox, filesystem, gettext) ->
    return {
        restrict: 'E'
        scope: {
            uploadpath: '='
            refresh: '='
            subdir: '=?'
            movetohome: '=?'
            owner: '=?'
            group: '=?'
        }
        template: (attrs) ->
            if (!attrs.target)
                target = "'/api/filesystem/upload'"
            else
                target = attrs.target
            return "<div>
                        <div    flow-init=\"{target: #{target}, chunkSize: 1024 * 1024, singleFile: true}\"
                                flow-files-submitted=\"onUploadBegin($flow)\"
                                ng-style=\"style\">
                            <input type=\"file\" flow-btn/>
                        </div>
                    </div>"

        link: ($scope) ->
            $scope.onUploadBegin = ($flow) -> 
                msg = messagebox.show({progress: true})
                filesystem.startFlowUpload($flow, $scope.uploadpath)
                .then () ->
                    if ($scope.owner and $scope.group)
                        filename=$flow.files[0].name
                        filepath=$scope.uploadpath+filename
                        $http.post('/api/lmn/chown', {filepath: $scope.uploadpath + $flow.files[0].name, owner: $scope.owner, group: $scope.group}).then () ->
                            if ($scope.movetohome)
                                $http.post('/api/lmn/session/moveFileToHome', {user: $scope.owner, filepath: $scope.uploadpath, subdir: $scope.subdir}).then (resp) ->
                                    $http.post('/api/lmn/remove-file', {filepath: filepath}).then () ->
                                        notify.success(gettext('Uploaded'))
                                        $scope.refresh()
                    else
                        notify.success(gettext('Uploaded'))
                    $scope.refresh()
                    msg.close()
                , null, (progress) -> 
                    msg.messagebox.title = 'Uploading: ' + Math.floor(100 * progress) + ' %'
    }

angular.module('lmn.common').directive 'lmButtonUpload', ($http, notify, messagebox, filesystem, gettext) ->
    return {
        restrict: 'E'
        scope: {
            uploadpath: '='
            btnlabel: '='
            refresh: '='
            subdir: '=?'
            movetohome: '=?'
            owner: '=?'
            group: '=?'
        }
        template: (attrs) -> 
            if (!attrs.target)
                target = "'/api/filesystem/upload'"
            else
                target = attrs.target
            return "<div>
                        <div    flow-init=\"{target: #{target}, chunkSize: 1024 * 1024, singleFile: true}\"
                                flow-files-submitted=\"onUploadBegin($flow)\"
                                ng-style=\"style\">
                            <span type=\"file\" flow-btn translate>{{btnlabel}}</span>
                        </div>
                    </div>"

        link: ($scope) ->

            $scope.onUploadBegin = ($flow) -> 
                msg = messagebox.show({progress: true})
                filesystem.startFlowUpload($flow, $scope.uploadpath)
                .then () ->
                    if ($scope.owner and $scope.group)
                        filename=$flow.files[0].name
                        filepath=$scope.uploadpath+filename
                        $http.post('/api/lmn/chown', {filepath: $scope.uploadpath + $flow.files[0].name, owner: $scope.owner, group: $scope.group}).then () ->
                            if ($scope.movetohome)
                                $http.post('/api/lmn/session/moveFileToHome', {user: $scope.owner, filepath: $scope.uploadpath, subdir: $scope.subdir}).then (resp) ->
                                    $http.post('/api/lmn/remove-file', {filepath: filepath}).then () ->
                                        notify.success(gettext('Uploaded'))
                                        $scope.refresh()
                    else
                        notify.success(gettext('Uploaded'))
                    $scope.refresh()
                    msg.close()
                , null, (progress) -> 
                    msg.messagebox.title = 'Uploading: ' + Math.floor(100 * progress) + ' %'
    }

### Examples in templates :

    <lm-drag-upload uploadpath="'/srv/'"></lm-drag-upload>
    <lm-button-upload uploadpath="'/root/'" btnlabel="'Upload SSH KEYS'"></lm-button-upload>
    <lm-select-upload uploadpath="'/home/toto'"></lm-select-upload>
###
# TODO handle multiple files
# TODO test translations
