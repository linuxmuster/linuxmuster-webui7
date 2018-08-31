angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/students',
        controller: 'LMUsersStudentsController'
        templateUrl: '/lm_users:resources/partial/students.html'

angular.module('lm.users').controller 'LMUsersStudentsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
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
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
       page: 1
       pageSize: 50


    $http.post('/api/lm/sophomorixUsers/students', {action: 'get-all'}).then (resp) ->
        $scope.students = resp.data

    $scope.showInitialPassword = (user) ->
        $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'get'}).then (resp) ->
            messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (user) ->
        $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'set-initial'}).then (resp) ->
            notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
        $http.post('/api/lm/users/password',{users: ( x['sAMAccountName'] for x in user ), action: 'set-random'}).then (resp) ->
            notify.success gettext('Random password set')

    $scope.setCustomPassword = (user) ->
        $uibModal.open(
            templateUrl: '/lm_users:resources/partial/customPassword.modal.html'
            controller: 'LMNUsersCustomPasswordController'
            size: 'mg'
            resolve:
                users: () -> user
        )
    $scope.userInfo = (user) ->
        $uibModal.open(
            templateUrl: '/lm_users:resources/partial/userDetails.modal.html'
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

    $scope.batchSetInitialPassword = () ->
        $scope.setInitialPassword((x for x in $scope.students when x.selected))

    $scope.batchSetRandomPassword = () ->
        $scope.setRandomPassword((x for x in $scope.students when x.selected))

    $scope.batchSetCustomPassword = () ->
        $scope.setCustomPassword((x for x in $scope.students when x.selected))

    $scope.selectAll = () ->
        for student in $scope.students
            student.selected = true


