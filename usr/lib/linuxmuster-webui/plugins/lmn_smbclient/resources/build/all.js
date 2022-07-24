'use strict';

angular.module('lmn.smbclient', ['core', 'flow']);


'use strict';

angular.module('lmn.smbclient').service('smbclient', function ($rootScope, $http, $q) {
    this.shares = function (user) {
        return $http.get('/api/lmn/smbclient/shares/' + user).then(function (response) {
            return response.data;
        });
    };

    // this.read = (path, encoding) =>
    //   $http.get(`/api/lmn/smbclient/read/${path}?encoding=${encoding || 'utf-8'}`).then(response => response.data)
    //
    // this.write = (path, content, encoding) =>
    //   $http.post(`/api/lmn/smbclient/write/${path}?encoding=${encoding || 'utf-8'}`, content).then(response => response.data)

    this.list = function (path) {
        return $http.post('/api/lmn/smbclient/list', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.delete_file = function (path) {
        return $http.post('/api/lmn/smbclient/file', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.move = function (src, dst) {
        return $http.post('/api/lmn/smbclient/move', { 'src': src, 'dst': dst }).then(function (response) {
            return response.data;
        });
    };

    this.copy = function (src, dst) {
        return $http.post('/api/lmn/smbclient/copy', { 'src': src, 'dst': dst }).then(function (response) {
            return response.data;
        });
    };

    this.delete_dir = function (path) {
        return $http.post('/api/lmn/smbclient/dir', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.stat = function (path) {
        return $http.get('/api/lmn/smbclient/stat/' + path).then(function (response) {
            return response.data;
        });
    };

    this.createFile = function (path) {
        return $http.post('/api/lmn/smbclient/create-file', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.createDirectory = function (path) {
        return $http.post('/api/lmn/smbclient/create-directory', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    //     this.downloadBlob = (content, mime, name) =>
    //         setTimeout(() => {
    //             let blob = new Blob([content], {type: mime});
    //             let elem = window.document.createElement('a');
    //             elem.href = URL.createObjectURL(blob);
    //             elem.download = name;
    //             document.body.appendChild(elem);
    //             elem.click();
    //             document.body.removeChild(elem);
    //         })
    //
    this.startFlowUpload = function ($flow, path) {
        q = $q.defer();
        $flow.on('fileProgress', function (file, chunk) {
            $rootScope.$apply(function () {
                // $flow.files may contain more than one file
                var uploadProgress = [];
                var _iteratorNormalCompletion = true;
                var _didIteratorError = false;
                var _iteratorError = undefined;

                try {
                    for (var _iterator = $flow.files[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                        var file = _step.value;

                        uploadProgress.push({
                            id: file.uniqueIdentifier, name: file.name, progress: Math.floor(100 * file.progress())
                        });
                    }
                } catch (err) {
                    _didIteratorError = true;
                    _iteratorError = err;
                } finally {
                    try {
                        if (!_iteratorNormalCompletion && _iterator.return) {
                            _iterator.return();
                        }
                    } finally {
                        if (_didIteratorError) {
                            throw _iteratorError;
                        }
                    }
                }

                q.notify(uploadProgress);
            });
        });
        $flow.on('complete', async function () {
            $flow.off('complete');
            $flow.off('fileProgress');
            var filesToFinish = [];
            var _iteratorNormalCompletion2 = true;
            var _didIteratorError2 = false;
            var _iteratorError2 = undefined;

            try {
                for (var _iterator2 = $flow.files[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                    var file = _step2.value;

                    filesToFinish.push({
                        id: file.uniqueIdentifier, path: path, name: file.name
                    });
                }
            } catch (err) {
                _didIteratorError2 = true;
                _iteratorError2 = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion2 && _iterator2.return) {
                        _iterator2.return();
                    }
                } finally {
                    if (_didIteratorError2) {
                        throw _iteratorError2;
                    }
                }
            }

            var response = await $http.post('/api/lmn/smbclient/finish-upload', filesToFinish);
            $rootScope.$apply(function () {
                q.resolve(response.data);
            });
            $flow.cancel();
        });
        $flow.upload();
        return q.promise;
    };

    return this;
});


// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lmn.smbclient').directive('smbUpload', function($http, $route, notify, messagebox, smbclient, gettext) {
    return {
      restrict: 'E',
      scope: {
        uploadpath: '@',
        reload: "=?",
        subdir: '=?'
      },
      replace: true,
      template: function(attrs) {
        var target;
        if (!attrs.target) {
          target = "'/api/lmn/smbclient/upload'";
        } else {
          target = attrs.target;
        }
        return `<div> <div class=\"col-md-1\"></div> <div class=\"col-md-10\"> <div    flow-init=\"{target: ${target}, chunkSize: 1024 * 1024}\" flow-files-submitted=\"onUploadBegin($flow)\" flow-drag-enter=\"class='dragdroparea-enter'\" flow-drag-leave=\"class='dragdroparea'\" ng-style=\"style\"> <div class=\"dragdroparea\" flow-drop style=\"border:dashed 1px orange;\"> <span translate>Drag and drop your files here</span> <span class=\"btn btn-lmn\" style=\"position:relative;top:20px;left:370px;\" flow-btn translate>Upload file</span> </div> <div ng-repeat=\"p in progress\" style=\"margin-top:10px;\" ng-show='p.progress < 100'> <span>{{p.name}} ({{p.progress}} %) </span> <smart-progress type=\"warning\" max=\"100\" value=\"p.progress\"></smart-progress> </div> </div> </div> <div class=\"col-md-1\"></div> </div>`;
      },
      link: function($scope, attrs) {
        return $scope.onUploadBegin = function($flow) {
          var file, i, len, ref;
          $scope.progress = [];
          $scope.files = [];
          ref = $flow.files;
          for (i = 0, len = ref.length; i < len; i++) {
            file = ref[i];
            $scope.files.push(file.name);
          }
          $scope.files_list = $scope.files.join(', ');
          return smbclient.startFlowUpload($flow, $scope.uploadpath).then(function(resp) {
            var desc, j, len1, results;
            notify.success(gettext('Uploaded ') + $scope.files_list);
            if ($scope.reload) {
// Add new file to samba listing without reloading the whole page
              results = [];
              for (j = 0, len1 = resp.length; j < len1; j++) {
                desc = resp[j];
                results.push($scope.$parent.items.push(desc));
              }
              return results;
            }
          }, null, function(progress) {
            return $scope.progress = progress.sort(function(a, b) {
              return a.name > b.name;
            });
          });
        };
      }
    };
  });

}).call(this);

