angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/users/globaladmins',
        controller: 'LMUsersGloballadminsController'
        templateUrl: '/lmn_users:resources/partial/globaladmins.html'

angular.module('lmn.users').controller 'LMUsersGloballadminsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, customFields, userPassword) ->
    pageTitle.set(gettext('Globaladmins'))

    $scope.sorts = [
     {
       name: gettext('Login')
       fx: (x) -> x.sAMAccountName
     }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
     page: 1
     pageSize: 50

    $scope.all_selected = false

    $http.get('/api/lmn/sophomorixUsers/globaladmins').then (resp) ->
        $scope.globaladmins = resp.data

    customFields.load_display('globaladministrators').then (resp) ->
        $scope.customDisplay = resp['customDisplay']
        $scope.customTitle = resp['customTitle']

    $scope.isListAttr = (attr) ->
        return customFields.isListAttr(attr)

    $http.get('/api/lmn/sophomorixUsers/bindusers/global').then (resp) ->
        $scope.globalbindusers = resp.data

    $scope.addGlobalBinduser = () ->
        messagebox.prompt(gettext('Login for new global bind user'), '').then (msg) ->
            # Filter chars ?
            $http.post('/api/lmn/sophomorixUsers/bindusers/global', {binduser: msg.value}).then (resp) ->
                notify.success(resp.data)
                $route.reload()

    $scope.deleteGlobalBinduser = (user) ->
        messagebox.show(title: gettext('Delete User'), text: gettext("Delete global bind user "+ ( x['sAMAccountName'] for x in user ) + '?'), positive: 'Delete', negative: 'Cancel').then () ->
            $http.patch('/api/lmn/sophomorixUsers/globaladmins', {users: ( x['sAMAccountName'] for x in user )}).then (resp) ->
                $route.reload()
                notify.success gettext('User deleted')

    $scope.showBindPW = userPassword.showBindPW
    $scope.showFirstPassword = (username) ->
        $scope.blurred = true
        userPassword.showFirstPassword(username).then((resp) ->
            $scope.blurred = false
        )
    $scope.resetFirstPassword = userPassword.resetFirstPassword
    $scope.setRandomFirstPassword = userPassword.setRandomFirstPassword
    $scope.setCustomPassword = userPassword.setCustomPassword
    $scope.batchResetFirstPassword = () -> userPassword.batchPasswords($scope.globaladmins, 'reset-first')
    $scope.batchSetRandomFirstPassword = () -> userPassword.batchPasswords($scope.globaladmins, 'random-first')
    $scope.batchSetCustomFirstPassword = () -> userPassword.batchPasswords($scope.globaladmins, 'custom-first')

    $scope.deleteGlobalAdmin = (user) ->
        messagebox.show(title: gettext('Delete User'), text: gettext("Delete global-administrator "+ ( x['sAMAccountName'] for x in user ) + '?'), positive: 'Delete', negative: 'Cancel').then () ->
            $http.patch('/api/lmn/sophomorixUsers/globaladmins', {users: ( x['sAMAccountName'] for x in user )}).then (resp) ->
                    $route.reload()
                    notify.success gettext('User deleted')

    $scope.addGlobalAdmin = () ->
      $uibModal.open(
        templateUrl: '/lmn_users:resources/partial/addAdmin.modal.html'
        controller: 'LMNUsersAddAdminController'
        size: 'mg'
        resolve:
          role: () -> 'globaladmin'
      )

    $scope.userInfo = (user) ->
      $uibModal.open(
        templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
        controller: 'LMNUserDetailsController'
        size: 'lg'
        resolve:
          id: () -> user[0]['sAMAccountName']
          role: () -> 'globaladmins'
          ).closed.then () ->
                $route.reload()

    $scope.editComment = (user) ->
        messagebox.prompt(gettext('Edit comment'), user.sophomorixComment).then (msg) ->
            $http.post("/api/lmn/sophomorixUsers/#{user.sAMAccountName}/comment", {comment: msg.value}).then (resp) ->
                $route.reload()

    $scope.haveSelection = () ->
        if $scope.globaladmins
            for x in $scope.globaladmins
                if x.selected
                    return true
        return false

    $scope.selectAll = (filter) ->
        if !filter?
            filter = ''
        for globaladmin in $scope.globaladmins
            if filter is undefined || filter == ''
                globaladmin.selected = $scope.all_selected
            if globaladmin.sn.toLowerCase().includes filter.toLowerCase()
                globaladmin.selected = $scope.all_selected
            if globaladmin.givenName.toLowerCase().includes filter.toLowerCase()
                globaladmin.selected = $scope.all_selected
            if globaladmin.sophomorixAdminClass.toLowerCase().includes filter.toLowerCase()
                globaladmin.selected = $scope.all_selected
            if globaladmin.sAMAccountName.toLowerCase().includes filter.toLowerCase()
                globaladmin.selected = $scope.all_selected



