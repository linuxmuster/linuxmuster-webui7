angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/globaladmins',
        controller: 'LMUsersGloballadminsController'
        templateUrl: '/lmn_users:resources/partial/globaladmins.html'

angular.module('lmn.users').controller 'LMUsersGloballadminsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
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

    $http.post('/api/lm/sophomorixUsers/globaladmins',{action: 'get-all'}).then (resp) ->
        $scope.globaladmins = resp.data

    $http.get('/api/lm/users/binduser/global').then (resp) ->
        $scope.globalbindusers = resp.data

    $scope.addGlobalBinduser = () ->
        messagebox.prompt(gettext('Login for new global bind user'), '').then (msg) ->
            # Filter chars ?
            $http.post('/api/lm/users/binduser/', {binduser: msg.value, level: 'global'}).then (resp) ->
                notify.success(resp.data)
                $route.reload()

    $scope.deleteGlobalBinduser = (user) ->
        messagebox.show(title: gettext('Delete User'), text: gettext("Delete global bind user "+ ( x['sAMAccountName'] for x in user ) + '?'), positive: 'Delete', negative: 'Cancel').then () ->
            $http.post('/api/lm/users/change-global-admin', {users: ( x['sAMAccountName'] for x in user ), action: 'delete'}).then (resp) ->
                $route.reload()
                notify.success gettext('User deleted')

    $scope.showInitialPassword = (user) ->
      $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'get'}).then (resp) ->
          $http.get('/api/lm/users/test-first-password/' + user[0]['sAMAccountName']).then (response) ->
            if response.data == true
                msg = gettext('Initial password (still set)')
            else
                msg = gettext('Initial password (changed from user)')
            messagebox.show(title: msg, text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (user) ->
      $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'set-initial'}).then (resp) ->
        notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
      $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'set-random'}).then (resp) ->
        notify.success gettext('Random password set')

    $scope.setCustomPassword = (user,type) ->
      $uibModal.open(
        templateUrl: '/lmn_users:resources/partial/customPassword.modal.html'
        controller: 'LMNUsersCustomPasswordController'
        size: 'mg'
        resolve:
          users: () -> user
          type: () -> type
      )

    $scope.deleteGlobalAdmin = (user) ->
        messagebox.show(title: gettext('Delete User'), text: gettext("Delete global-administrator "+ ( x['sAMAccountName'] for x in user ) + '?'), positive: 'Delete', negative: 'Cancel').then () ->
            $http.post('/api/lm/users/change-global-admin', {users: ( x['sAMAccountName'] for x in user ), action: 'delete'}).then (resp) ->
                    $route.reload()
                    notify.success gettext('User deleted')


    $scope.addGlobalAdmin = () ->
      $uibModal.open(
        templateUrl: '/lmn_users:resources/partial/addAdmin.modal.html'
        controller: 'LMNUsersAddAdminController'
        size: 'mg'
        resolve:
          role: () -> angular.copy('global-admin')
      )
    $scope.userInfo = (user) ->
      console.log (user)
      $uibModal.open(
        templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
        controller: 'LMNUserDetailsController'
        size: 'lg'
        resolve:
          id: () -> user[0]['sAMAccountName']
          role: () -> 'globaladmins'
          )


    $scope.haveSelection = () ->
        if $scope.globaladmins
            for x in $scope.globaladmins
                if x.selected
                    return true
        return false

    $scope.batchSetInitialPassword = () ->
        $scope.setInitialPassword((x for x in $scope.globaladmins when x.selected))

    $scope.batchSetRandomPassword = () ->
        $scope.setRandomPassword((x for x in $scope.globaladmins when x.selected))

    $scope.batchSetCustomPassword = () ->
        $scope.setCustomPassword((x for x in $scope.globaladmins when x.selected))

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



