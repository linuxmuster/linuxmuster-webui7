angular.module('lmn.samba_share').service('samba_share', function($rootScope, $http, $q) {
    // this.shares = () =>
    //   $http.get("/api/lmn/samba_share/shares").then(response => response.data)
    //
    // this.read = (path, encoding) =>
    //   $http.get(`/api/lmn/samba_share/read/${path}?encoding=${encoding || 'utf-8'}`).then(response => response.data)
    //
    // this.write = (path, content, encoding) =>
    //   $http.post(`/api/lmn/samba_share/write/${path}?encoding=${encoding || 'utf-8'}`, content).then(response => response.data)

    this.list = (path) =>
        $http.post(`/api/lmn/samba_share/list`, {'path': path}).then(response => response.data)

    this.delete_file = (path) =>
        $http.post(`/api/lmn/samba_share/file/`, {'path': path}).then(response => response.data)

    this.delete_dir = (path) =>
        $http.post(`/api/lmn/samba_share/dir/`, {'path':path}).then(response => response.data)

    this.stat = (path) =>
        $http.get(`/api/lmn/samba_share/stat/${path}`).then(response => response.data)

    this.createFile = (path) =>
        $http.post(`/api/lmn/samba_share/create-file/`, {'path':path}).then(response => response.data)

    this.createDirectory = (path) =>
        $http.post(`/api/lmn/samba_share/create-directory`, {'path':path}).then(response => response.data)

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
//     this.startFlowUpload = ($flow, path) => {
//         q = $q.defer()
//         $flow.on('fileProgress', (file, chunk) => {
//             $rootScope.$apply(() => {
//                 // $flow.files may contain more than one file
//                 var uploadProgress = []
//                 for (var file of $flow.files) {
//                     uploadProgress.push({
//                         id: file.uniqueIdentifier, name: file.name, progress: Math.floor(100*file.progress())
//                     })
//                 }
//                 q.notify(uploadProgress)
//             })
//         })
//         $flow.on('complete', async () => {
//             $flow.off('complete')
//             $flow.off('fileProgress')
//             let filesToFinish = []
//             for (var file of $flow.files) {
//                 filesToFinish.push({
//                     id: file.uniqueIdentifier, path, name: file.name
//                 })
//             }
//             let response = await $http.post(`/api/lmn/samba_share/finish-upload`, filesToFinish)
//             $rootScope.$apply(() => {
//                 q.resolve(response.data)
//             })
//             $flow.cancel()
//         })
//         $flow.upload()
//         return q.promise
//     }
//
//     return this;
});
