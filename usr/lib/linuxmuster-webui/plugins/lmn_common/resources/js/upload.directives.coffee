angular.module('lm.common').directive 'lmDragUpload', ($http, notify, messagebox, filesystem, gettext) ->
    return {
        restrict: 'E'
        scope: {
            uploadpath: '='
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
                            <div class=\"dragdroparea\" flow-drop  ng-class=\"class\" translate>
                                Drag And Drop your file here
                            </div>
                        </div>
                    </div>"

        link: ($scope, attrs) ->
            $scope.onUploadBegin = ($flow) ->
                msg = messagebox.show({progress: true})
                filesystem.startFlowUpload($flow, $scope.uploadpath)
                .then () ->
                    notify.success(gettext('Uploaded'))
                    msg.close()
                , null, (progress) -> 
                    msg.messagebox.title = ':) Uploading: ' + Math.floor(100 * progress) + ' %'
    }

angular.module('lm.common').directive 'lmSelectUpload', ($http, notify, messagebox, filesystem, gettext) ->
    return {
        restrict: 'E'
        scope: {
            uploadpath: '='
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
                    notify.success(gettext('Uploaded'))
                    msg.close()
                , null, (progress) -> 
                    msg.messagebox.title = 'Uploading: ' + Math.floor(100 * progress) + ' %'
    }

angular.module('lm.common').directive 'lmButtonUpload', ($http, notify, messagebox, filesystem, gettext) ->
    return {
        restrict: 'E'
        scope: {
            uploadpath: '='
            btnlabel: '='
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
                    notify.success(gettext('Uploaded'))
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
