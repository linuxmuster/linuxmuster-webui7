angular.module('lmn.smbclient').directive 'smbUpload', ($http, $route, notify, messagebox, smbclient, gettext) ->
    return {
        restrict: 'E'
        scope: {
            uploadpath: '@'
            reload: "=?"
            subdir: '=?'
        }
        replace: true
        template: (attrs) ->
            if (!attrs.target)
                target = "'/api/lmn/smbclient/upload'"
            else
                target = attrs.target
            return "<div>
                        <div class=\"col-md-2\"></div>
                        <div class=\"col-md-8\">
                            <div    flow-init=\"{target: #{target}, chunkSize: 1024 * 1024}\"
                                    flow-files-submitted=\"onUploadBegin($flow)\"
                                    flow-drag-enter=\"class='dragdroparea-enter'\"
                                    flow-drag-leave=\"class='dragdroparea'\"
                                    ng-style=\"style\">
                                <div class=\"dragdroparea\" flow-drop  style='border:dashed 1px orange'>
                                    <span class=\"btn btn-default\" flow-btn translate>Upload file</span>
                                    <span translate> or drag And Drop your file here</span>
                                </div>
                                <div ng-repeat=\"p in progress\">
                                    <span>{{p.name}} ({{p.progress}} %) </span>
                                    <smart-progress type=\"warning\" max=\"100\" value=\"p.progress\"></smart-progress>
                                </div>
                            </div>
                        </div>
                        <div class=\"col-md-2\"></div>
                    </div>"

        link: ($scope, attrs) ->
            $scope.onUploadBegin = ($flow) ->
                $scope.progress = []
                $scope.files = []
                for file in $flow.files
                    $scope.files.push(file.name)
                $scope.files_list = $scope.files.join(', ')
                smbclient.startFlowUpload($flow, $scope.uploadpath)
                .then () ->
                    notify.success(gettext('Uploaded ') + $scope.files_list)
                    if $scope.reload
                        $route.reload()
                , null, (progress) ->
                    $scope.progress = progress.sort((a,b) -> a.name > b.name)
    }