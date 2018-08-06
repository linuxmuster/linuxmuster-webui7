angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/students',
        controller: 'LMUsersStudentsController'
        templateUrl: '/lm_users:resources/partial/students.html'

angular.module('lm.users').controller 'LMUsersStudentsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Students'))

    $http.get("/api/lm/sophomorixUsers/students").then (resp) ->
        $scope.students = resp.data

    $scope.showInitialPassword = (user) ->
        username = (user[0]['sAMAccountName'])
        $http.post('/api/lm/users/password', {user: username, action: 'get'}).then (resp) ->
            messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (user) ->
        username = (user[0]['sAMAccountName'])
        $http.post('/api/lm/users/password', {user: username, action: 'set-initial'}).then (resp) ->
            notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
        #username = (user[0]['sAMAccountName'])
        $http.post('/api/lm/users/password',{users: (x[0]['sAMAccountName'] for x in user), action: 'set-random'}).then (resp) ->
            console.log (x[0]['sAMAccountName'])
            notify.success gettext('Random password set')

    $scope.setCustomPassword = (user) ->
        username = (user[0]['sAMAccountName'])
        $uibModal.open(
            templateUrl: '/lm_users:resources/partial/customPassword.modal.html'
            controller: 'LMNUsersCustomPasswordController'
            size: 'mg'
            resolve:
                user: () -> username
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


