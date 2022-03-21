'use strict';

angular.module('lmn.samba_share', ['core', 'flow']);


'use strict';

angular.module('lmn.samba_share').service('samba_share', function ($rootScope, $http, $q) {
    this.shares = function () {
        return $http.get("/api/lmn/samba_share/shares").then(function (response) {
            return response.data;
        });
    };

    this.read = function (path, encoding) {
        return $http.get('/api/lmn/samba_share/read/' + path + '?encoding=' + (encoding || 'utf-8')).then(function (response) {
            return response.data;
        });
    };

    this.write = function (path, content, encoding) {
        return $http.post('/api/lmn/samba_share/write/' + path + '?encoding=' + (encoding || 'utf-8'), content).then(function (response) {
            return response.data;
        });
    };

    this.list = function (path) {
        return $http.post('/api/lmn/samba_share/list', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.delete_file = function (path) {
        return $http.post('/api/lmn/samba_share/unlink', { 'path': path }).then(function (response) {
            return response.data;
        });
    };

    this.delete_dir = function (path) {
        return $http.delete('/api/lmn/samba_share/dir/' + path).then(function (response) {
            return response.data;
        });
    };

    this.stat = function (path) {
        return $http.get('/api/lmn/samba_share/stat/' + path).then(function (response) {
            return response.data;
        });
    };

    this.chmod = function (path, mode) {
        return $http.post('/api/lmn/samba_share/chmod/' + path, { mode: mode }).then(function (response) {
            return response.data;
        });
    };

    this.createFile = function (path) {
        return $http.post('/api/lmn/samba_share/create-file/' + path);
    };

    this.createDirectory = function (path) {
        return $http.post('/api/lmn/samba_share/create-directory/' + path);
    };

    this.downloadBlob = function (content, mime, name) {
        return setTimeout(function () {
            var blob = new Blob([content], { type: mime });
            var elem = window.document.createElement('a');
            elem.href = URL.createObjectURL(blob);
            elem.download = name;
            document.body.appendChild(elem);
            elem.click();
            document.body.removeChild(elem);
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

            var response = await $http.post('/api/lmn/samba_share/finish-upload', filesToFinish);
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


