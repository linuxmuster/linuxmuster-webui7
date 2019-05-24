isStrongPwd1 = (password) ->
      regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}/
      validPassword = regExp.test(password)
      return validPassword


angular.module('lm.users').controller 'LMNUsersCustomPasswordController', ($scope, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, users) ->
    $scope.username = users
    $scope.save = (userpw) ->
        if not $scope.userpw
            notify.error gettext("You have to enter a password")
            return
        if not isStrongPwd1($scope.userpw)
           notify.error gettext("Password too weak")
           return
        else
            $http.post('/api/lm/users/password', {users: (x['sAMAccountName'] for x in users), action: 'set', password: $scope.userpw}).then (resp) ->
                notify.success gettext('New password set')
        $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()

angular.module('lm.users').controller 'LMNUserDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, id, role) ->

    #notify.error gettext("You have to enter a username")
    $scope.id = id

    $http.post('/api/lm/sophomorixUsers/'+role, {action: 'get-specified', user: id}).then (resp) ->
        $scope.userDetails = resp.data
        console.log ($scope.userDetails)

    $scope.close = () ->
        $uibModalInstance.dismiss()

angular.module('lm.users').controller 'LMUsersUploadModalController', ($scope, $window, $http, $uibModalInstance, messagebox, notify, $uibModal, gettext, filesystem, userlist) ->
    $scope.path = "/tmp/"
    $scope.onUploadBegin = ($flow) ->
        $uibModalInstance.close()
        msg = messagebox.show({progress: true})
        filesystem.startFlowUpload($flow, $scope.path).then(() ->
            notify.success(gettext('Uploaded'))
            filename = $flow["files"][0]["name"]

            #$http.post('/api/lmn/sophomorixUsers/new-file', {path: '/tmp/'+filename, userlist: userlist}).then (resp) ->
            #    console.log (resp['data'])
            #    if resp['data'][0] == 'ERROR'
            #        notify.error (resp['data'][1])
            #    if resp['data'][0] == 'LOG'
            #        notify.success gettext(resp['data'][1])
            #    # TODO: it would be better to reload just the content frame. Currently I dont know how to set the route to reload it
            #    $window.location.reload()
            #    msg.close()
        , null, (progress) ->
          msg.messagebox.title = "Uploading: #{Math.floor(100 * progress)}%"
        )

    $scope.close = () ->
        $uibModalInstance.close()

angular.module('lm.users').controller 'LMNUsersAddAdminController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, role) ->

    $scope.role = role
    $scope.save = (username) ->
        if not $scope.username
            notify.error gettext("You have to enter a username")
            return
        else
            notify.success gettext('Adding administrator...')
            $http.post('/api/lm/users/change-'+role, {action: 'create' ,users: username}).then (resp) ->
                # console.log (resp.data)
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                $route.reload()
            $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()
