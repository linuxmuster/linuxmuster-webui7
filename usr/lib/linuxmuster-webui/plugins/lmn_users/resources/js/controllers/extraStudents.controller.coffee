angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/users/extra-students',
        controller: 'LMUsersExtraStudentsController'
        templateUrl: '/lmn_users:resources/partial/extra-students.html'


angular.module('lmn.users').controller 'LMUsersExtraStudentsController', ($scope, $http, $uibModal, $route, gettext, notify, pageTitle, lmEncodingMap, lmFileEditor, lmFileBackups, validation) ->
    pageTitle.set(gettext('Extra Students'))

    $scope.sorts = [
        {
            name: gettext('Class')
            fx: (x) -> x.class
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
        {
            name: gettext('Login')
            fx: (x) -> x.login
        }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
        page: 1
        pageSize: 100

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
        if filter == 'students'
            valid = valid && ($scope.students.filter(validation.findval('login', val)).length < 2)
        if valid
            return ""
        if isnew and !$scope.first_save
            return "has-error-new"
        else
            return "has-error"

    $http.get('/api/lmn/schoolsettings').then (resp) ->
        $scope.encoding = lmEncodingMap[resp.data.encoding_students_extra] or 'ISO8859-1'
        $http.get("/api/lmn/users/lists/extrastudents?encoding=#{$scope.encoding}").then (resp) ->
            $scope.students = resp.data

    $scope.add = () ->
        if $scope.students.length > 0
            $scope.paging.page = Math.floor(($scope.students.length - 1) / $scope.paging.pageSize) + 1
        $scope.students.push {_isNew: true}

    $scope.remove = (student) ->
        $scope.students.remove(student)

    $scope.editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/extrastudents.csv', $scope.encoding).then () ->
            $route.reload()
            
    $scope.numErrors = () ->
        return document.getElementsByClassName("has-error").length + document.getElementsByClassName("has-error-new").length > 0

    $scope.save = () ->
        if $scope.numErrors()
            $scope.first_save = true
            angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
            notify.error('Required data missing')
            return
        return $http.post("/api/lmn/users/lists/extrastudents?encoding=#{$scope.encoding}", $scope.students).then () ->
            notify.success 'Saved'

    $scope.saveAndCheck = () ->
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/check.modal.html'
                controller: 'LMUsersCheckModalController'
                backdrop: 'static'
            )

    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/extrastudents.csv', $scope.encoding)
