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
                        <div class=\"col-md-1\"></div>
                        <div class=\"col-md-10\">
                            <div    flow-init=\"{target: #{target}, chunkSize: 1024 * 1024}\"
                                    flow-files-submitted=\"onUploadBegin($flow)\">
                                <div class=\"dragdroparea\"
                                     flow-drop
                                     flow-drag-enter=\"class='dragdroparea-enter'\"
                                     flow-drag-leave=\"class='dragdroparea'\"
                                     ng-class=\"class\">
                                    <span translate>Drag and drop your files here</span>
                                    <span class=\"btn btn-lmn btn-upload\" flow-btn translate>
                                        Upload file
                                    </span>
                                </div>
                                <div ng-repeat=\"p in progress\" style=\"margin-top:10px;\" ng-show='p.progress < 100'>
                                    <span>{{p.name}} ({{p.progress}} %) </span>
                                    <smart-progress type=\"warning\" max=\"100\" value=\"p.progress\"></smart-progress>
                                </div>
                            </div>
                        </div>
                        <div class=\"col-md-1\"></div>
                    </div>"

        link: ($scope, attrs) ->
            $scope.onUploadBegin = ($flow) ->
                $scope.progress = []
                $scope.files = []
                for file in $flow.files
                    $scope.files.push(file.name)
                $scope.files_list = $scope.files.join(', ')
                smbclient.startFlowUpload($flow, $scope.uploadpath)
                .then (resp) ->
                    notify.success(gettext('Uploaded ') + $scope.files_list)
                    if $scope.reload
                        # Add new file to samba listing without reloading the whole page
                        for desc in resp
                            $scope.$parent.items.push(desc)

                , null, (progress) ->
                    $scope.progress = progress.sort((a,b) -> a.name > b.name)
    }