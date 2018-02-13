angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/ati-teacher-passwords',
        controller: 'LMUsersATiTeacherPasswordsController'
        templateUrl: '/lm_users:resources/partial/ati-teacher-passwords.html'


angular.module('lm.users').controller 'LMUsersATiTeacherPasswordsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Teachers'))

    $scope.sorts = [
        {
            name: gettext('Login name')
            fx: (x) -> x.sAMAccountName
        }
        {
            name: gettext('Lastname')
            fx: (x) -> x.sn
        }
        {
            name: gettext('Firstname')
            fx: (x) -> x.givenName
        }
        {
            name: gettext('Email')
            fx: (x) -> x.mail
        }
    ]

    $scope.fields = {
        sAMAccountName:
            visible: true
            name: gettext('Loginname')
        sn:
            visible: true
            name: gettext('Lastname')
        givenName:
            visible: true
            name: gettext('Firstname')
        mail:
            visible: true
            name: gettext('Email')
        sophomorixFirstPassword:
            visible: false
            name: gettext('Initial Password')
        sophomorixBirthdate:
            visible: false
            name: gettext('Birthdate')
    }


    $scope.sort = $scope.sorts[0]
    $scope.paging =
        page: 1
        pageSize: 20

    $scope.add = () ->
        $scope.paging.page = Math.floor(($scope.students.length - 1) / $scope.paging.pageSize) + 1
        $scope.filter = ''
        $scope.students.push {first_name: 'New', _isNew: true}


    $http.get("/api/lm/sophomorixUsers/teachers").then (resp) ->
        $scope.teachers = resp.data


## legacy functions
    $scope.showInitialPassword = (teachers) ->
        #console.log teachers                          # ATi What we Send {sAMAccountName: "schoen", $$hashKey: "object:318"}
        $http.post('/api/lm/users/password', {users: (x.sAMAccountName for x in teachers), action: 'get'}).then (resp) ->
            messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')

    $scope.showEmail = (teachers) ->
        #console.log teachers                          # ATi What we Send {sAMAccountName: "schoen", $$hashKey: "object:318"}
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




