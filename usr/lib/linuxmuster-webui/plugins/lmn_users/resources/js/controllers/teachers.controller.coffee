angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/teachers',
        controller: 'LMUsersTeachersController'
        templateUrl: '/lmn_users:resources/partial/teachers.html'

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
      {
        name: gettext('Status')
        fx: (x) -> x.sophomorixStatus.tag
      }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
      page: 1
      pageSize: 50


    $http.post('/api/lm/sophomorixUsers/teachers',{action: 'get-all'}).then (resp) ->
        $scope.teachers = resp.data

    $scope.showInitialPassword = (users) ->
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
    $scope.teachersQuota = false
    $scope.getQuotas = () ->
        teacherList = (t.sAMAccountName for t in $scope.teachers)
        $http.post('/api/lm/users/get-group-quota',{groupList: teacherList}).then (resp) ->
            $scope.teachersQuota = resp.data
            console.log($scope.teachersQuota)



    $scope.setInitialPassword = (user) ->
       $http.post('/api/lm/users/password', {users: (x['sAMAccountName'] for x in user), action: 'set-initial'}).then (resp) ->
          notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
       $http.post('/api/lm/users/password', {users: (x['sAMAccountName'] for x in user), action: 'set-random'}).then (resp) ->
          notify.success gettext('Random password set')

    $scope.setCustomPassword = (user,type) ->
       $uibModal.open(
          templateUrl: '/lmn_users:resources/partial/customPassword.modal.html'
          controller: 'LMNUsersCustomPasswordController'
          size: 'mg'
          resolve:
             users: () -> user
             type: () -> type
       )
    $scope.userInfo = (user) ->
       console.log (user)
       $uibModal.open(
          templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
          controller: 'LMNUserDetailsController'
          size: 'lg'
          resolve:
             id: () -> user[0]['sAMAccountName']
             role: () -> 'teachers'
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

    $scope.selectAll = (filter) ->
        if !filter?
            filter = ''
        for teacher in $scope.teachers
           if filter is undefined
              teacher.selected = true
           if teacher.sn.toLowerCase().includes filter.toLowerCase()
              teacher.selected = true
           if teacher.givenName.toLowerCase().includes filter.toLowerCase()
              teacher.selected = true
           if teacher.sophomorixAdminClass.toLowerCase().includes filter.toLowerCase()
              teacher.selected = true
           if teacher.sAMAccountName.toLowerCase().includes filter.toLowerCase()
              teacher.selected = true
