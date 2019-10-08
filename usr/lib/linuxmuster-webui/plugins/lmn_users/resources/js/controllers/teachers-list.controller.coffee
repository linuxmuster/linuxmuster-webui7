angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/teachers-list',
        controller: 'LMUsersTeachersListController'
        templateUrl: '/lmn_users:resources/partial/teachers-list.html'


angular.module('lm.users').controller 'LMUsersTeachersListController', ($scope, $http, $location, $route, $uibModal, gettext, lmEncodingMap, notify, messagebox, pageTitle, lmFileEditor, lmFileBackups, validation) ->
    pageTitle.set(gettext('Teachers'))

    $scope.sorts = [
        {
            name: gettext('Login')
            fx: (x) -> x.login
        }
        {
            name: gettext('First name')
            fx: (x) -> x.first_name
        }
        {
            name: gettext('Last name')
            fx: (x) -> x.last_name
        }
        {
            name: gettext('Birthday')
            fx: (x) -> x.birthday
        }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
        page: 1
        pageSize: 100

    $scope.fields = {
        last_name:
            visible: true
            name: gettext('Last Name')
        first_name:
            visible: true
            name: gettext('First Name')
        birthday:
            visible: true
            name: gettext('Birthday')
        password:
            visible: false
            name: gettext('Desired Password')
        login:
            visible: true
            name: gettext('Login')
    }


    $http.get('/api/lm/schoolsettings').then (resp) ->
        school = 'default-school'
        $scope.encoding = resp.data["userfile.teachers.csv"].encoding
        if $scope.encoding is 'auto'
            $http.post('/api/lmn/schoolsettings/determine-encoding', {path: '/etc/linuxmuster/sophomorix/'+school+'/teachers.csv'}).then (response) ->
                if response.data is 'unknown'
                    $scope.encoding = 'utf-8'
                else
                    $scope.encoding = response.data
        $http.get("/api/lm/users/teachers-list?encoding=#{$scope.encoding}").then (resp) ->
            $scope.teachers = resp.data

    $scope.first_save = false

    $scope.validateField = (name, val, isnew, filter=null) ->
        # TODO : what valid chars for class, name and course ?
        # Temporary solution : not filter these fields
        if name == 'TODO'
            return ""

        # TODO : is pasword necessary for extra course ? Filtered only if not undefined.
        # Desired passwords will be marked if not strong enough, is it necessary for extra courses ?
        if name == 'Password' and !val
            return ""
            
        valid = validation["isValid"+name](val) && val
        if filter == 'teachers'
            valid = valid && ($scope.teachers.filter(validation.findval('login', val)).length < 2)
            
        if valid
            return ""
        if isnew and !$scope.first_save
            return "has-error-new"
        else
            return "has-error"

    $scope.add = () ->
        if $scope.teachers.length > 0
            $scope.paging.page = Math.floor(($scope.teachers.length - 1) / $scope.paging.pageSize) + 1
        $scope.filter = ''
        $scope.teachers.push {class: 'Lehrer', _isNew: true}

    $scope.remove = (teacher) ->
        $scope.teachers.remove(teacher)

    $scope.editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/teachers.csv', 'ISO8859-1').then () ->
            $route.reload()

    $scope.numErrors = () ->
        return document.getElementsByClassName("has-error").length + document.getElementsByClassName("has-error-new").length > 0

    $scope.save = () ->
        if $scope.numErrors()
            $scope.first_save = true
            angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
            notify.error('Required data missing')
            return
        return $http.post("/api/lm/users/teachers-list?encoding=#{$scope.encoding}", $scope.teachers).then () ->
            notify.success gettext('Saved')

    $scope.saveAndCheck = () ->
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/check.modal.html'
                controller: 'LMUsersCheckModalController'
                backdrop: 'static'
            )

    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/teachers.csv', $scope.encoding)

    $scope.confirmUpload = () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/upload.modal.html'
                controller: 'LMUsersUploadModalController'
                backdrop: 'static'
                resolve:
                    userlist: () -> 'teachers.csv'
            )
