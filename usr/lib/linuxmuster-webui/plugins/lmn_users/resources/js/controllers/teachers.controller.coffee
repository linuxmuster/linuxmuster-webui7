angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/teachers',
        controller: 'LMUsersTeachersController'
        templateUrl: '/lm_users:resources/partial/teachers.html'

angular.module('lm.users').controller 'LMUsersTeachersController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Teachers'))

    $scope.sorts = [
      {
        name: gettext('First name')
        fx: (x) -> x.givenName
      }
      {
        name: gettext('Last name')
        fx: (x) -> x.sn
      }
      {
        name: gettext('Login')
        fx: (x) -> x.sAMAccountName
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


    $http.get("/api/lm/sophomorixUsers/teachers").then (resp) ->
        $scope.teachers = resp.data

    $scope.showInitialPassword = (user) ->
       $http.post('/api/lm/users/password', {users: ( x['sAMAccountName'] for x in user ), action: 'get'}).then (resp) ->
          messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')


    $scope.setInitialPassword = (user) ->
       $http.post('/api/lm/users/password', {users: (x['sAMAccountName'] for x in user), action: 'set-initial'}).then (resp) ->
          notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
       $http.post('/api/lm/users/password', {users: (x['sAMAccountName'] for x in user), action: 'set-random'}).then (resp) ->
          notify.success gettext('Random password set')

    $scope.setCustomPassword = (user) ->
       $uibModal.open(
          templateUrl: '/lm_users:resources/partial/customPassword.modal.html'
          controller: 'LMNUsersCustomPasswordController'
          size: 'mg'
          resolve:
             users: () -> user
       )

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

