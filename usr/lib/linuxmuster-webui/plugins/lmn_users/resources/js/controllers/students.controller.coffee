angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/students',
        controller: 'LMUsersStudentsController'
        templateUrl: '/lm_users:resources/partial/students.html'


angular.module('lm.users').controller 'LMUsersStudentsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Students'))

    $http.get("/api/lm/sophomorixUsers/students").then (resp) ->
        $scope.students = resp.data


## legacy functions
    $scope.showInitialPassword = (students) ->
        #console.log students                          # ATi What we Send {sAMAccountName: "schoen", $$hashKey: "object:318"}
        $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in students), action: 'get'}).then (resp) ->
            messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (students) ->
        $http.post('/api/lm/sophomorixUsers/password', {users: (x.sAMAccountName for x in students), action: 'set-initial'}).then (resp) ->
            notify.success gettext('Initial password set')

    $scope.setRandomPassword = (students) ->
        $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in students), action: 'set-random'}).then (resp) ->
            text = ("#{x.user}: #{x.password}" for x in resp.data).join(',\n')
            messagebox.show(title: gettext('New password'), text: text, positive: 'OK')

    $scope.setCustomPassword = (students) ->
        messagebox.prompt(gettext('New password')).then (msg) ->
            if not msg.value
                return
            $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in students), action: 'set', password: msg.value}).then (resp) ->
                notify.success gettext('New password set')

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




