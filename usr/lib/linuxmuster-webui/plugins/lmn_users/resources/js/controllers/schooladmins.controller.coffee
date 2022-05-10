angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/schooladmins',
        controller: 'LMUsersSchooladminsController'
        templateUrl: '/lmn_users:resources/partial/schooladmins.html'

angular.module('lmn.users').controller 'LMUsersSchooladminsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, customFields) ->
    pageTitle.set(gettext('Schooladmins'))

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

    $http.post('/api/lm/sophomorixUsers/schooladmins',{action: 'get-all'}).then (resp) ->
        $scope.schooladmins = resp.data

    customFields.load_display('schooladministrators').then (resp) ->
        $scope.customDisplay = resp['customDisplay']
        $scope.customTitle = resp['customTitle']

    $scope.isListAttr = (attr) ->
        return customFields.isListAttr(attr)

    $http.get('/api/lm/users/binduser/school').then (resp) ->
        $scope.schoolbindusers = resp.data

    $scope.addSchoolBinduser = () ->
        messagebox.prompt(gettext('Login for new school bind user'), '').then (msg) ->
            # Filter chars ?
            $http.post('/api/lm/users/binduser/', {binduser: msg.value, level: 'school'}).then (resp) ->
                notify.success(resp.data)
                $route.reload()

    $scope.deleteSchoolBinduser = (user) ->
        messagebox.show(title: gettext('Delete User'), text: gettext("Delete school bind user "+ ( x['sAMAccountName'] for x in user ) + '?'), positive: 'Delete', negative: 'Cancel').then () ->
            $http.post('/api/lm/users/change-global-admin', {users: ( x['sAMAccountName'] for x in user ), action: 'delete'}).then (resp) ->
                $route.reload()
                notify.success gettext('User deleted')

    $scope.showPW = (user) ->
       messagebox.show(title: gettext('Show bind user password'), text: gettext("Do you really want to see this password ? It could be a security issue!"), positive: 'Show', negative: 'Cancel').then () ->
            $http.post('/api/lm/users/showBindPW', {user: user.sAMAccountName}).then (resp) ->
                messagebox.show(title: gettext('Show bind user password'), text: resp.data, positive: 'OK')

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

    $scope.deleteSchoolAdmin = (user) ->
        messagebox.show(title: gettext('Delete User'), text: gettext("Delete school-administrator "+ ( x['sAMAccountName'] for x in user ) + '?'), positive: 'Delete', negative: 'Cancel').then () ->
            $http.post('/api/lm/users/change-school-admin', {users: ( x['sAMAccountName'] for x in user ), action: 'delete'}).then (resp) ->
                $route.reload()
                notify.success gettext('User deleted')


    $scope.addSchoolAdmin = () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/addAdmin.modal.html'
                controller: 'LMNUsersAddAdminController'
                size: 'mg'
                resolve:
                    role: () -> 'school-admin'
            )

    $scope.userInfo = (user) ->
      console.log (user)
      $uibModal.open(
        templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
        controller: 'LMNUserDetailsController'
        size: 'lg'
        resolve:
          id: () -> user[0]['sAMAccountName']
          role: () -> 'schooladmins'
          ).closed.then () ->
                $route.reload()


    $scope.haveSelection = () ->
        if $scope.schooladmins
            for x in $scope.schooladmins
                if x.selected
                    return true
        return false

    $scope.batchSetInitialPassword = () ->
        $scope.setInitialPassword((x for x in $scope.schooladmins when x.selected))

    $scope.batchSetRandomPassword = () ->
        $scope.setRandomPassword((x for x in $scope.schooladmins when x.selected))

    $scope.batchSetCustomPassword = () ->
        $scope.setCustomPassword((x for x in $scope.schooladmins when x.selected))

    $scope.selectAll = (filter) ->
        if !filter?
            filter = ''
        for schooladmin in $scope.schooladmins
            if filter is undefined || filter == ''
                schooladmin.selected = $scope.all_selected
            if schooladmin.sn.toLowerCase().includes filter.toLowerCase()
                schooladmin.selected = $scope.all_selected
            if schooladmin.givenName.toLowerCase().includes filter.toLowerCase()
                schooladmin.selected = $scope.all_selected
            if schooladmin.sophomorixAdminClass.toLowerCase().includes filter.toLowerCase()
                schooladmin.selected = $scope.all_selected
            if schooladmin.sAMAccountName.toLowerCase().includes filter.toLowerCase()
                schooladmin.selected = $scope.all_selected




