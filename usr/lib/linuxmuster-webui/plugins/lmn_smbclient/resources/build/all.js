'use strict';

angular.module('lmn.smbclient', ['core', 'flow']);


'use strict';

angular.module('lmn.smbclient').service('smbclient', function ($rootScope, $http, $q, gettext, notify, messagebox) {
    this.shares = function (user) {
        return $http.get('/api/lmn/smbclient/shares/' + user).then(function (response) {
            return response.data;
        });
    };

    this.list = function (path) {
        return $http.post('/api/lmn/smbclient/list', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.listhome = function (user) {
        return $http.post('/api/lmn/smbclient/listhome', { 'user': user }).then(function (response) {
            return response.data;
        });
    };

    this.delete_file = function (path) {
        return $http.post('/api/lmn/smbclient/unlink', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.move = function (src, dst) {
        var notify_success = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : true;

        return $http.post('/api/lmn/smbclient/move', { 'src': src, 'dst': dst }).then(function (response) {
            if (notify_success) {
                notify.success(src + gettext(' moved!'));
            }
            return response.data;
        }, function (response) {
            notify.error(response.data.message);
        });
    };

    this.copy = function (src, dst) {
        var notify_success = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : true;

        return $http.post('/api/lmn/smbclient/copy', { 'src': src, 'dst': dst }).then(function (response) {
            if (notify_success) {
                notify.success(src + gettext(' copied!'));
            }
            return response.data;
        }, function (response) {
            notify.error(response.data.message);
        });
    };

    this.delete_dir = function (path) {
        return $http.post('/api/lmn/smbclient/rmdir', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.stat = function (path) {
        return $http.get('/api/lmn/smbclient/stat/' + path).then(function (response) {
            return response.data;
        });
    };

    this.createFile = function (path) {
        return $http.post('/api/lmn/smbclient/file', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.createDirectory = function (path) {
        return $http.post('/api/lmn/smbclient/directory', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

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

    this.refresh_krbcc = function () {
        return messagebox.prompt("Please give your password:", "", "password").then(function (msg) {
            return $http.post('/api/lmn/smbclient/refresh_krbcc', { 'pw': msg.value }).then(function (resp) {
                if (resp.data.type == "error") {
                    notify.error(resp.data.msg);
                    return $q.reject();
                } else {
                    notify.success(resp.data.msg);
                }
            });
        });
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
        return `<div> <div class=\"col-md-1\"></div> <div class=\"col-md-10\"> <div    flow-init=\"{target: ${target}, chunkSize: 1024 * 1024}\" flow-files-submitted=\"onUploadBegin($flow)\"> <div class=\"dragdroparea\" flow-drop flow-drag-enter=\"class='dragdroparea-enter'\" flow-drag-leave=\"class='dragdroparea'\" ng-class=\"class\"> <span translate>Drag and drop your files here</span> <span class=\"btn btn-lmn btn-upload\" flow-btn translate> Upload file </span> </div> <div ng-repeat=\"p in progress\" style=\"margin-top:10px;\" ng-show='p.progress < 100'> <span>{{p.name}} ({{p.progress}} %) </span> <smart-progress type=\"warning\" max=\"100\" value=\"p.progress\"></smart-progress> </div> </div> </div> <div class=\"col-md-1\"></div> </div>`;
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

