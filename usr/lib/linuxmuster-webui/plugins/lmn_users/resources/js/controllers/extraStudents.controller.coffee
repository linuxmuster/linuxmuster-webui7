angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/extra-students',
        controller: 'LMUsersExtraStudentsController'
        templateUrl: '/lmn_users:resources/partial/extra-students.html'


angular.module('lm.users').controller 'LMUsersExtraStudentsController', ($scope, $http, $uibModal, $route, gettext, notify, pageTitle, lmEncodingMap, lmFileEditor, lmFileBackups) ->
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

    $scope.validateField = (name, val, isnew) ->
        valid = $scope["isValid"+name](val) && val
        if valid
            return ""
        if isnew and !$scope.first_save
            return "has-error-new"
        else
            return "has-error"

    $scope.findval = (attr, val) ->
        return (dict) ->
            dict[attr] == val
    
    $scope.isValidClass = (cl) ->
        regExp = /^([0-9a-zA-Z]*)$/ 
        validClass = regExp.test(cl)
        return true ## TODO : valid chars for a classname ?
    
    $scope.isValidLogin = (login) ->
        regExp = /^([0-9a-zA-Z]*)$/ 
        validLogin = regExp.test(login) && ($scope.students.filter($scope.findval('login', login)).length < 2)
        return true ## TODO : valid chars for a login ?
    
    $scope.isValidName = (name) ->
        regExp = /^([0-9a-zA-Z]*)$/ 
        validName = regExp.test(name)
        return true ## TODO : valid chars for a name ?
    
    $scope.isValidBirthday = (birthday) ->
        regExp = /^(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.](19|20)\d\d$/ ## Not perfect : allows 31.02.1920, but not so important
        validBirthday = regExp.test(birthday)
        return validBirthday

    $http.get('/api/lm/schoolsettings').then (resp) ->
        $scope.encoding = lmEncodingMap[resp.data.encoding_students_extra] or 'ISO8859-1'
        $http.get("/api/lm/users/extra-students?encoding=#{$scope.encoding}").then (resp) ->
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
        return $http.post("/api/lm/users/extra-students?encoding=#{$scope.encoding}", $scope.students).then () ->
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
