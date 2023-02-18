angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/users/teachers',
        controller: 'LMUsersTeachersController'
        templateUrl: '/lmn_users:resources/partial/teachers.html'

angular.module('lmn.users').controller 'LMUsersTeachersController', ($q, $scope, $http, $location, $route, $uibModal, $sce, gettext, notify, messagebox, pageTitle, customFields, userPassword) ->
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

    $scope.all_selected = false
    $scope.query = ''

    $http.get('/api/lmn/sophomorixUsers/teachers').then (resp) ->
        $scope.teachers = resp.data

    customFields.load_display('teachers').then (resp) ->
        $scope.customDisplay = resp['customDisplay']
        $scope.customTitle = resp['customTitle']

    $scope.isListAttr = (attr) ->
        return customFields.isListAttr(attr)

    $scope.teachersQuota = false
    $scope.getQuotas = () ->
        teacherList = (t.sAMAccountName for t in $scope.teachers)
        promises = []
        for teacher in teacherList
            promises.push($http.get("/api/lmn/quota/usermap/#{teacher}"))
        $q.all(promises).then (resp) ->
            $scope.teachersQuota = {}
            for teacher in resp
                login = Object.keys(teacher.data)[0]
                $scope.teachersQuota[login] = teacher.data[login]

    $scope.showFirstPassword = (username) ->
        $scope.blurred = true
        userPassword.showFirstPassword(username).then((resp) ->
            $scope.blurred = false
        )
    $scope.resetFirstPassword = userPassword.resetFirstPassword
    $scope.setRandomFirstPassword = userPassword.setRandomFirstPassword
    $scope.setCustomPassword = userPassword.setCustomPassword
    $scope.batchResetFirstPassword = () -> userPassword.batchPasswords($scope.teachers, 'reset-first')
    $scope.batchSetRandomFirstPassword = () -> userPassword.batchPasswords($scope.teachers, 'random-first')
    $scope.batchSetCustomFirstPassword = () -> userPassword.batchPasswords($scope.teachers, 'custom-first')
    $scope.printSelectedPasswords = () -> userPassword.printSelectedPasswords($scope.teachers)

    $scope.userInfo = (user) ->
       $uibModal.open(
          templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
          controller: 'LMNUserDetailsController'
          size: 'lg'
          resolve:
             id: () -> user[0]['sAMAccountName']
             role: () -> 'teachers'
             ).closed.then () ->
                $route.reload()

    $scope.haveSelection = () ->
        if $scope.teachers
            for x in $scope.teachers
                if x.selected
                    return true
        return false

    $scope.filter = (row) ->
        # Only query sAMAccountName, givenName and sn
        result = false
        for value in ['sAMAccountName', 'givenName', 'sn']
            if (row[value] != undefined)
                result = result || row[value].toLowerCase().indexOf($scope.query.toLowerCase() || '') != -1
        return result

    $scope.selectAll = (query) ->
        if !query?
            query = ''
        for teacher in $scope.teachers
           if query is undefined || query == ''
              teacher.selected = $scope.all_selected
           if teacher.sn.toLowerCase().includes query.toLowerCase()
              teacher.selected = $scope.all_selected
           if teacher.givenName.toLowerCase().includes query.toLowerCase()
              teacher.selected = $scope.all_selected
           if teacher.sophomorixAdminClass.toLowerCase().includes query.toLowerCase()
              teacher.selected = $scope.all_selected
           if teacher.sAMAccountName.toLowerCase().includes query.toLowerCase()
              teacher.selected = $scope.all_selected
