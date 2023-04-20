angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/users/schooladmins',
        controller: 'LMUsersSchooladminsController'
        templateUrl: '/lmn_users:resources/partial/schooladmins.html'

angular.module('lmn.users').controller 'LMUsersSchooladminsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, customFields, userPassword) ->
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

    $http.get('/api/lmn/sophomorixUsers/schooladmins').then (resp) ->
        $scope.schooladmins = resp.data

    customFields.load_display('schooladministrators').then (resp) ->
        $scope.customDisplay = resp['customDisplay']
        $scope.customTitle = resp['customTitle']

    $scope.isListAttr = (attr) ->
        return customFields.isListAttr(attr)

    $http.get('/api/lmn/sophomorixUsers/bindusers/school').then (resp) ->
        $scope.schoolbindusers = resp.data

    $scope.addSchoolBinduser = () ->
        messagebox.prompt(gettext('Login for new school bind user'), '').then (msg) ->
            # Filter chars ?
            $http.post('/api/lmn/sophomorixUsers/bindusers/school', {binduser: msg.value}).then (resp) ->
                notify.success(resp.data)
                $route.reload()

    $scope.deleteSchoolBinduser = (user) ->
        messagebox.show(title: gettext('Delete User'), text: gettext("Delete school bind user "+ ( x['sAMAccountName'] for x in user ) + '?'), positive: 'Delete', negative: 'Cancel').then () ->
            $http.patch('/api/lmn/sophomorixUsers/schooladmins', {users: ( x['sAMAccountName'] for x in user )}).then (resp) ->
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
    $scope.batchResetFirstPassword = () -> userPassword.batchPasswords($scope.schooladmins, 'reset-first')
    $scope.batchSetRandomFirstPassword = () -> userPassword.batchPasswords($scope.schooladmins, 'random-first')
    $scope.batchSetCustomFirstPassword = () -> userPassword.batchPasswords($scope.schooladmins, 'custom-first')

    $scope.deleteSchoolAdmin = (user) ->
        messagebox.show(title: gettext('Delete User'), text: gettext("Delete school-administrator "+ ( x['sAMAccountName'] for x in user ) + '?'), positive: 'Delete', negative: 'Cancel').then () ->
            $http.patch('/api/lmn/sophomorixUsers/schooladmins', {users: ( x['sAMAccountName'] for x in user )}).then (resp) ->
                $route.reload()
                notify.success gettext('User deleted')


    $scope.addSchoolAdmin = () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/addAdmin.modal.html'
                controller: 'LMNUsersAddAdminController'
                size: 'mg'
                resolve:
                    role: () -> 'schooladmin'
            )

    $scope.userInfo = (user) ->
      $uibModal.open(
        templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
        controller: 'LMNUserDetailsController'
        size: 'lg'
        resolve:
          id: () -> user[0]['sAMAccountName']
          role: () -> 'schooladmins'
          ).closed.then () ->
                $route.reload()

    $scope.editComment = (user) ->
        messagebox.prompt(gettext('Edit comment'), user.sophomorixComment).then (msg) ->
            $http.post("/api/lmn/sophomorixUsers/#{user.sAMAccountName}/comment", {comment: msg.value}).then (resp) ->
                $route.reload()

    $scope.haveSelection = () ->
        if $scope.schooladmins
            for x in $scope.schooladmins
                if x.selected
                    return true
        return false

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




