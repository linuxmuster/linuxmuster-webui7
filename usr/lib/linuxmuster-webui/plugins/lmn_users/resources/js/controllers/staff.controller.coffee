angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/users/staff',
        controller: 'LMUsersParentsController'
        templateUrl: '/lmn_users:resources/partial/staff.html'

angular.module('lmn.users').controller 'LMUsersParentsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, customFields, userPassword) ->
    pageTitle.set(gettext('Parents'))

    $scope.sorts = [
       {
          name: gettext('Class')
          fx: (x) -> x.sophomorixAdminClass
       }
       {
          name: gettext('First name')
          fx: (x) -> x.givenName
       }
       {
          name: gettext('Last name')
          fx: (x) -> x.sn
       }
       {
          name: gettext('Birthday')
          fx: (x) -> x.sophomorixBirthdate
       }
       {
          name: gettext('Status')
          fx: (x) -> x.sophomorixStatus.tag
       }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
       page: 1
       pageSize: 50

    $scope.all_selected = false
    $scope.query = ''

    customFields.load_display('staff').then (resp) ->
        $scope.customDisplay = resp['customDisplay']
        $scope.customTitle = resp['customTitle']

    $scope.isListAttr = (attr) ->
        return customFields.isListAttr(attr)

    $http.get('/api/lmn/sophomorixUsers/staff').then (resp) ->
        $scope.staff = resp.data

    $scope.showFirstPassword = (username) ->
        $scope.blurred = true
        userPassword.showFirstPassword(username).then((resp) ->
            $scope.blurred = false
        )
    $scope.resetFirstPassword = userPassword.resetFirstPassword
    $scope.setRandomFirstPassword = userPassword.setRandomFirstPassword
    $scope.setCustomPassword = userPassword.setCustomPassword
    $scope.batchResetFirstPassword = () -> userPassword.batchPasswords($scope.staff, 'reset-first')
    $scope.batchSetRandomFirstPassword = () -> userPassword.batchPasswords($scope.staff, 'random-first')
    $scope.batchSetCustomFirstPassword = () -> userPassword.batchPasswords($scope.staff, 'custom-first')
    $scope.printSelectedPasswords = () -> userPassword.printSelectedPasswords($scope.staff)

    $scope.userInfo = (user) ->
        $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
            controller: 'LMNUserDetailsController'
            size: 'lg'
            resolve:
                id: () -> user[0]['sAMAccountName']
                role: () -> 'staff'
                )

    $scope.haveSelection = () ->
        if $scope.staff
            for x in $scope.staff
                if x.selected
                    return true
        return false

    $scope.filter = (row) ->
        # Only query sAMAccountName, givenName, sn and sophomorixAdminClass
        result = false
        for value in ['sAMAccountName', 'givenName', 'sn', 'sophomorixAdminClass']
            if (row[value] != undefined)
                result = result || row[value].toLowerCase().indexOf($scope.query.toLowerCase() || '') != -1
        return result

    $scope.selectAll = (query) ->
        if !query?
            query = ''
        for st in $scope.staff
            if query is undefined || query == ''
                st.selected = $scope.all_selected
            if st.sn.toLowerCase().includes query.toLowerCase()
                st.selected = $scope.all_selected
            if st.givenName.toLowerCase().includes query.toLowerCase()
                st.selected = $scope.all_selected
            if st.sophomorixAdminClass.toLowerCase().includes query.toLowerCase()
                st.selected = $scope.all_selected
            if st.sAMAccountName.toLowerCase().includes query.toLowerCase()
                st.selected = $scope.all_selected


