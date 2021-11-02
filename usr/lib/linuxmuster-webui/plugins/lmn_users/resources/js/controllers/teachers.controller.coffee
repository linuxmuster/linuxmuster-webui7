angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/teachers',
        controller: 'LMUsersTeachersController'
        templateUrl: '/lmn_users:resources/partial/teachers.html'

angular.module('lmn.users').controller 'LMUsersTeachersController', ($q, $scope, $http, $location, $route, $uibModal, $sce, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
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

    $scope.list_attr_enabled = ['proxyAddresses']
    for n in [1,2,3,4,5]
        $scope.list_attr_enabled.push('sophomorixCustomMulti' + n)

    $http.post('/api/lm/sophomorixUsers/teachers',{action: 'get-all'}).then (resp) ->
        $scope.teachers = resp.data

    $http.get('/api/lm/read_custom_config').then (resp) ->
        $scope.customDisplay = resp.data.customDisplay.teachers
        if ($scope.customDisplay?)
            $scope.customTitle = ['',]
            for idx in [1,2,3]
                if $scope.customDisplay[idx] == undefined or $scope.customDisplay[idx] == ''
                    $scope.customTitle.push('')
                else if $scope.customDisplay[idx] == 'proxyAddresses'
                    $scope.customTitle.push(resp.data.proxyAddresses.teachers.title)
                else
                    index = $scope.customDisplay[idx].slice(-1)
                    if $scope.isListAttr($scope.customDisplay[idx])
                        $scope.customTitle.push(resp.data.customMulti.teachers[index].title || '')
                    else
                        $scope.customTitle.push(resp.data.custom.teachers[index].title || '')

    $scope.isListAttr = (attr_name) ->
        return $scope.list_attr_enabled.includes(attr_name)

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
        promises = []
        for teacher in teacherList
            promises.push($http.post('/api/lm/users/get-group-quota',{groupList: [teacher]}))
        $q.all(promises).then (resp) ->
            $scope.teachersQuota = {}
            for teacher in resp
                login = Object.keys(teacher.data)[0]
                $scope.teachersQuota[login] = teacher.data[login]

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
             ).closed.then () ->
                $route.reload()



    $scope.haveSelection = () ->
        if $scope.teachers
            for x in $scope.teachers
                if x.selected
                    return true
        return false

    $scope.printSelectedPasswords = () ->
        msg = messagebox.show(progress: true)
        user_list = (x.sAMAccountName for x in $scope.teachers when x.selected)
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
        $scope.setInitialPassword((x for x in $scope.teachers when x.selected))

    $scope.batchSetRandomPassword = () ->
        $scope.setRandomPassword((x for x in $scope.teachers when x.selected))

    $scope.batchSetCustomPassword = () ->
        $scope.setCustomPassword((x for x in $scope.teachers when x.selected))

    $scope.filter = (row) ->
        if row isnt 'none'
            # Only query sAMAccountName, givenName and sn
            result = false
            for value in ['sAMAccountName', 'givenName', 'sn']
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
