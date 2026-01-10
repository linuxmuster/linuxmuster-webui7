angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/users/students',
        controller: 'LMUsersStudentsController'
        templateUrl: '/lmn_users:resources/partial/students.html'

angular.module('lmn.users').controller 'LMUsersStudentsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, customFields, userPassword) ->
    pageTitle.set(gettext('Students'))

    $scope.activeTab = 0
    $scope.tabs = ['students', 'attic']

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

    $scope.selected = {
      'students': false,
      'attic': false
    }

    $scope.query = ''
    $scope.show_attic = false
    $scope.show_students = false

    customFields.load_display('students').then (resp) ->
        $scope.customDisplay = resp['customDisplay']
        $scope.customTitle = resp['customTitle']

    $scope.isListAttr = (attr) ->
        return customFields.isListAttr(attr)

    $http.get('/api/lmn/sophomorixUsers/students').then (resp) ->
        $scope.students = resp.data.filter((s) -> s.sophomorixAdminClass != 'attic')
        $scope.show_students = true
        $scope.attic = resp.data.filter((s) -> s.sophomorixAdminClass == 'attic')
        $scope.show_attic = $scope.attic.length > 0

    $scope.showFirstPassword = (username) ->
        $scope.blurred = true
        userPassword.showFirstPassword(username).then((resp) ->
            $scope.blurred = false
        )
    $scope.resetFirstPassword = userPassword.resetFirstPassword
    $scope.setRandomFirstPassword = userPassword.setRandomFirstPassword
    $scope.setCustomPassword = userPassword.setCustomPassword
    $scope.batchResetFirstPassword = () -> userPassword.batchPasswords($scope.students, 'reset-first')
    $scope.batchSetRandomFirstPassword = () -> userPassword.batchPasswords($scope.students, 'random-first')
    $scope.batchSetCustomFirstPassword = () -> userPassword.batchPasswords($scope.students, 'custom-first')
    $scope.printSelectedPasswords = () -> userPassword.printSelectedPasswords($scope.students)

    $scope.batchAtticResetFirstPassword = () -> userPassword.batchPasswords($scope.attic, 'reset-first')
    $scope.batchAtticSetRandomFirstPassword = () -> userPassword.batchPasswords($scope.attic, 'random-first')
    $scope.batchAtticSetCustomFirstPassword = () -> userPassword.batchPasswords($scope.attic, 'custom-first')
    $scope.printAtticSelectedPasswords = () -> userPassword.printSelectedPasswords($scope.attic)

    $scope.userInfo = (user) ->
        $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
            controller: 'LMNUserDetailsController'
            size: 'lg'
            resolve:
                id: () -> user[0]['sAMAccountName']
                role: () -> 'students'
                )

    $scope.studentsSelected = () ->
        if $scope.students
            for x in $scope.students
                if x.selected
                    return true
        return false

    $scope.atticSelected = () ->
        if $scope.attic
            for x in $scope.attic
                if x.selected
                    return true
        return false

    $scope.killstudent = (user_cn) ->
        messagebox.show(
          title: gettext('Kill user ' + user_cn),
          text: gettext("Do you really want to definitively remove the user #{user_cn}? This action is uncoverable." ),
          positive: 'Yes, definitively remove',
          negative: 'Cancel').then () ->
            $http.post('/api/lmn/sophomorixUsers/killuser', {user: user_cn}).then (resp) ->
                console.log(resp.data)
                if resp.data == true
                    notify.success(gettext("User #{user_cn} successfully deleted!"))
                    messagebox.show(
                        title: gettext('Clean up students.csv'),
                        text: gettext('The user account was deleted but you will have to manually remove the corresponding line in the file students.csv.'),
                        positive: 'OK, I understand',
                    )
                else
                    notify.error("There was an error during the process. Please try manually to execute the command 'sophomorix-kill --kill #{user_cn}' to get more informations.")

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
                student.selected = $scope.selected.students
            if student.sn.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.selected.students
            if student.givenName.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.selected.students
            if student.sophomorixAdminClass.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.selected.students
            if student.sAMAccountName.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.selected.students

    $scope.selectAllAttic = (query) ->
        if !query?
            query = ''
        for student in $scope.attic
            if query is undefined || query == ''
                student.selected = $scope.selected.attic
            if student.sn.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.selected.attic
            if student.givenName.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.selected.attic
            if student.sophomorixAdminClass.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.selected.attic
            if student.sAMAccountName.toLowerCase().includes query.toLowerCase()
                student.selected = $scope.selected.attic


