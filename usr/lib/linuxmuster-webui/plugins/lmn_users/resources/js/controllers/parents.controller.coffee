angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/users/parents',
        controller: 'LMUsersParentsController'
        templateUrl: '/lmn_users:resources/partial/parents.html'

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

    customFields.load_display('parents').then (resp) ->
        $scope.customDisplay = resp['customDisplay']
        $scope.customTitle = resp['customTitle']

    $scope.isListAttr = (attr) ->
        return customFields.isListAttr(attr)

    $http.get('/api/lmn/sophomorixUsers/parents').then (resp) ->
        $scope.parents = resp.data

    $scope.showFirstPassword = (username) ->
        $scope.blurred = true
        userPassword.showFirstPassword(username).then((resp) ->
            $scope.blurred = false
        )
    $scope.resetFirstPassword = userPassword.resetFirstPassword
    $scope.setRandomFirstPassword = userPassword.setRandomFirstPassword
    $scope.setCustomPassword = userPassword.setCustomPassword
    $scope.batchResetFirstPassword = () -> userPassword.batchPasswords($scope.parents, 'reset-first')
    $scope.batchSetRandomFirstPassword = () -> userPassword.batchPasswords($scope.parents, 'random-first')
    $scope.batchSetCustomFirstPassword = () -> userPassword.batchPasswords($scope.parents, 'custom-first')
    $scope.printSelectedPasswords = () -> userPassword.printSelectedPasswords($scope.parents)

    $scope.userInfo = (user) ->
        $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
            controller: 'LMNUserDetailsController'
            size: 'lg'
            resolve:
                id: () -> user[0]['sAMAccountName']
                role: () -> 'parents'
                )

    $scope.haveSelection = () ->
        if $scope.parents
            for x in $scope.parents
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
        for parent in $scope.parents
            if query is undefined || query == ''
                parent.selected = $scope.all_selected
            if parent.sn.toLowerCase().includes query.toLowerCase()
                parent.selected = $scope.all_selected
            if parent.givenName.toLowerCase().includes query.toLowerCase()
                parent.selected = $scope.all_selected
            if parent.sophomorixAdminClass.toLowerCase().includes query.toLowerCase()
                parent.selected = $scope.all_selected
            if parent.sAMAccountName.toLowerCase().includes query.toLowerCase()
                parent.selected = $scope.all_selected


