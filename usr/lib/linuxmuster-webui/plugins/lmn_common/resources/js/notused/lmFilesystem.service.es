angular.module('lmn.common').service('lmfilesystem', function($rootScope, $http, $q) {
    this.startFlowUpload = ($flow, path) => {
       q = $q.defer()
       $flow.on('fileProgress', (file, chunk) => {
          $rootScope.$apply(() => {
             q.notify($flow.files[0].progress())
          })
       })
       $flow.on('complete', async () => {
          $flow.off('complete')
          $flow.off('fileProgress')
          let response = await $http.post(`/api/lmn/filesystem/userupload`, {
             id: $flow.files[0].uniqueIdentifier, path, name: $flow.files[0].name
          })
          $rootScope.$apply(() => {
             q.resolve(response.data)
          })
          $flow.cancel()
       })

       $flow.upload()
       return q.promise
    }

    return this;
});

