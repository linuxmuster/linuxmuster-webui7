angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/teachers',
        controller: 'LMUsersTeachersController'
        templateUrl: '/lm_users:resources/partial/teachers.html'


angular.module('lm.users').controller 'LMUsersTeachersController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Teachers'))

    $http.get("/api/lm/sophomorixUsers/teachers").then (resp) ->
        $scope.teachers = resp.data


## legacy functions
    $scope.showInitialPassword = (teachers) ->
        #console.log teachers                          # ATi What we Send {sAMAccountName: "schoen", $$hashKey: "object:318"}
        $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in teachers), action: 'get'}).then (resp) ->
            messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (teachers) ->
        $http.post('/api/lm/sophomorixUsers/password', {users: (x.sAMAccountName for x in teachers), action: 'set-initial'}).then (resp) ->
            notify.success gettext('Initial password set')

    $scope.setRandomPassword = (teachers) ->
        $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in teachers), action: 'set-random'}).then (resp) ->
            text = ("#{x.user}: #{x.password}" for x in resp.data).join(',\n')
            messagebox.show(title: gettext('New password'), text: text, positive: 'OK')

    $scope.setCustomPassword = (teachers) ->
        messagebox.prompt(gettext('New password')).then (msg) ->
            if not msg.value
                return
            $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in teachers), action: 'set', password: msg.value}).then (resp) ->
                notify.success gettext('New password set')

    $scope.haveSelection = () ->
        if $scope.teachers
            for x in $scope.teachers
                if x.selected
                    return true
        return false

    $scope.batchSetInitialPassword = () ->
        $scope.setInitialPassword((x for x in $scope.teachers when x.selected))

    $scope.batchSetRandomPassword = () ->
        $scope.setRandomPassword((x for x in $scope.teachers when x.selected))

    $scope.batchSetCustomPassword = () ->
        $scope.setCustomPassword((x for x in $scope.teachers when x.selected))

    $scope.selectAll = () ->
        for teacher in $scope.teachers
            teacher.selected = true




