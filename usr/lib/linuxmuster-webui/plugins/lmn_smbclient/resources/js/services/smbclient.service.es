angular.module('lmn.smbclient').service('smbclient', function($rootScope, $http, $q, gettext, notify, messagebox) {
    this.shares = (user) =>
      $http.get(`/api/lmn/smbclient/shares/${user}`).then(response => response.data)

    this.list = (path) =>
        $http.post(`/api/lmn/smbclient/list`, {'path': path}).then(response => response.data)

    this.listhome = (user) =>
        $http.post(`/api/lmn/smbclient/listhome`, {'user': user}).then(response => response.data)

    this.delete_file = (path) =>
        $http.post(`/api/lmn/smbclient/unlink`, {'path': path}).then(response => response.data)

    this.move = (src, dst, notify_success=true) => {
        return $http.post(`/api/lmn/smbclient/move`, {'src': src, 'dst':dst}).then((response) => {
            if (notify_success) {
                notify.success(src + gettext(' moved!'));
            }
            return response.data;
        }, (response) => {
            notify.error(response.data.message);
        });
    };

    this.copy = (src, dst, notify_success=true) => {
        return $http.post(`/api/lmn/smbclient/copy`, {'src': src, 'dst':dst}).then((response) => {
            if (notify_success) {
                notify.success(src + gettext(' copied!'));
            }
            return response.data;
        }, (response) => {
            notify.error(response.data.message);
        });
    };

    this.delete_dir = (path) =>
        $http.post(`/api/lmn/smbclient/rmdir`, {'path':path}).then(response => response.data)

    this.stat = (path) =>
        $http.get(`/api/lmn/smbclient/stat/${path}`).then(response => response.data)

    this.createFile = (path) =>
        $http.post(`/api/lmn/smbclient/file`, {'path':path}).then(response => response.data)

    this.createDirectory = (path) =>
        $http.post(`/api/lmn/smbclient/directory`, {'path':path}).then(response => response.data)

    this.startFlowUpload = ($flow, path) => {
        q = $q.defer()
        $flow.on('fileProgress', (file, chunk) => {
            $rootScope.$apply(() => {
                // $flow.files may contain more than one file
                var uploadProgress = []
                for (var file of $flow.files) {
                    uploadProgress.push({
                        id: file.uniqueIdentifier, name: file.name, progress: Math.floor(100*file.progress())
                    })
                }
                q.notify(uploadProgress)
            })
        })
        $flow.on('complete', async () => {
            $flow.off('complete')
            $flow.off('fileProgress')
            let filesToFinish = []
            for (var file of $flow.files) {
                filesToFinish.push({
                    id: file.uniqueIdentifier, path, name: file.name
                })
            }
            let response = await $http.post(`/api/lmn/smbclient/finish-upload`, filesToFinish)
            $rootScope.$apply(() => {
                q.resolve(response.data)
            })
            $flow.cancel()
        })
        $flow.upload()
        return q.promise
    }

    this.refresh_krbcc = () => {
        return messagebox.prompt("Please give your password:", "", "password").then((msg) => {
            return $http.post('/api/lmn/smbclient/refresh_krbcc', {'pw': msg.value}).then((resp) => {
                if (resp.data.type == "error") {
                    notify.error(resp.data.msg);
                    return $q.reject();
                } else {
                    notify.success(resp.data.msg);
                }
            });
        });
    }

    return this;
});
