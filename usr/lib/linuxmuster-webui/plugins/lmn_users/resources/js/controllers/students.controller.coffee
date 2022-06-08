angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/students',
        controller: 'LMUsersStudentsController'
        templateUrl: '/lmn_users:resources/partial/students.html'

angular.module('lmn.users').controller 'LMUsersStudentsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, customFields) ->
    pageTitle.set(gettext('Students'))

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

    customFields.load_display('students').then (resp) ->
        $scope.customDisplay = resp['customDisplay']
        $scope.customTitle = resp['customTitle']

    $scope.isListAttr = (attr) ->
        return customFields.isListAttr(attr)

    $http.post('/api/lm/sophomorixUsers/students', {action: 'get-all'}).then (resp) ->
        $scope.students = resp.data

    $scope.showInitialPassword = (users) ->
        console.log (users)
        user=[]
        user[0]=users[0]["sAMAccountName"]
        # function needs an array which contains user on first position
        type=gettext('Initial password')
        $uibModal.open(
           templateUrl: '/lmn_users:resources/partial/showPassword.modal.html'
           controller: 'LMNUsersShowPasswordController'
           resolve:
              user: () -> user
              type: () -> type
        )



    $scope.setInitialPassword = (user) ->
        $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'set-initial'}).then (resp) ->
            notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
        $http.post('/api/lm/users/password',{users: ( x['sAMAccountName'] for x in user ), action: 'set-random'}).then (resp) ->
            notify.success gettext('Random password set')

    $scope.setCustomPassword = (user, type) ->
        $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/customPassword.modal.html'
            controller: 'LMNUsersCustomPasswordController'
            size: 'mg'
            resolve:
                users: () -> user
                type: () -> type
        )
    $scope.userInfo = (user) ->
        $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
            controller: 'LMNUserDetailsController'
            size: 'lg'
            resolve:
                id: () -> user[0]['sAMAccountName']
                role: () -> 'students'
                )


    $scope.haveSelection = () ->
        if $scope.students
            for x in $scope.students
                if x.selected
                    return true
        return false

    $scope.printSelectedPasswords = () ->
        msg = messagebox.show(progress: true)
        user_list = (x.sAMAccountName for x in $scope.students when x.selected)
        $http.post('/api/lm/users/print-individual', {user: $scope.identity.user, user_list: user_list}).then (resp) ->
            console.log(resp.data)
            if resp.data == 'success'
                notify.success(gettext("Created password pdf"))
                location.href = "/api/lm/users/print-download/user-#{$scope.identity.user}.pdf"
            else
                notify.error(gettext("Could not create password pdf"))
        .finally () ->
            msg.close()

    $scope.batchSetInitialPassword = () ->
        $scope.setInitialPassword((x for x in $scope.students when x.selected))

    $scope.batchSetRandomPassword = () ->
        $scope.setRandomPassword((x for x in $scope.students when x.selected))

    $scope.batchSetCustomPassword = () ->
        $scope.setCustomPassword((x for x in $scope.students when x.selected))

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
        for student in $scope.students
            if query is undefined || query == ''
                student.selected = $scope.all_selected
            if student.sn.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.all_selected
            if student.givenName.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.all_selected
            if student.sophomorixAdminClass.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.all_selected
            if student.sAMAccountName.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.all_selected


