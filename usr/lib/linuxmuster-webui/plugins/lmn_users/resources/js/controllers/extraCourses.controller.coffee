angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/extra-courses',
        controller: 'LMUsersExtraCoursesController'
        templateUrl: '/lmn_users:resources/partial/extra-courses.html'


angular.module('lm.users').controller 'LMUsersExtraCoursesController', ($scope, $http, $uibModal, $route, notify, gettext, pageTitle, lmEncodingMap, lmFileEditor, lmFileBackups) ->
    pageTitle.set(gettext('Extra Courses'))

    $scope.sorts = [
        {
            name: gettext('Course')
            fx: (x) -> x.course
        }
        {
            name: gettext('Base name')
            fx: (x) -> x.base_name
        }
        {
            name: gettext('Birthday')
            fx: (x) -> x.birthday
        }
        {
            name: gettext('Count')
            fx: (x) -> x.count
        }
        {
            name: gettext('GECOS')
            fx: (x) -> x.gecos
        }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
        page: 1
        pageSize: 100

    $http.get('/api/lm/schoolsettings').then (resp) ->
        $scope.encoding = lmEncodingMap[resp.data.encoding_courses_extra] or 'ISO8859-1'
        $http.get("/api/lm/users/extra-courses?encoding=#{$scope.encoding}").then (resp) ->
            $scope.courses = resp.data

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
    
    $scope.isValidCourse = (course) ->
        regExp = /^([0-9a-zA-Z]*)$/ 
        validCourse = regExp.test(course)
        return true ## TODO : valid chars for a classname ?
    
    $scope.isValidCount = (count) ->
        regExp = /^([0-9]*)$/ 
        validCount = regExp.test(count)
        return validCount
        
    $scope.isStrongPwd = (password) ->
        regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}/
        validPassword = regExp.test(password)
        return validPassword

    $scope.validCharPwd =(password) ->
        regExp = /^[a-zA-Z0-9!@#§+\-$%&*{}()\]\[]+$/
        validPassword = regExp.test(password)
        return validPassword
    
    $scope.isValidPassword = (password) ->
        return $scope.validCharPwd(password) && $scope.isStrongPwd(password)
    
    $scope.isValidName = (name) ->
        regExp = /^([0-9a-zA-Z]*)$/ 
        validName = regExp.test(name)
        return true ## TODO : valid chars for a name ?
    
    $scope.isValidBirthday = (birthday) ->
        regExp = /^(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.](19|20)\d\d$/ ## Not perfect : allows 31.02.1920, but not so important
        validBirthday = regExp.test(birthday)
        return validBirthday
        
    $scope.isValidDate = (date) ->
        regExp = /^(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.](19|20)\d\d$/ ## Not perfect : allows 31.02.1920, but not so important
        validDate = regExp.test(date)
        return validDate

    $scope.add = () ->
        if $scope.courses.length > 0
            $scope.paging.page = Math.floor(($scope.courses.length - 1) / $scope.paging.pageSize) + 1
        $scope.courses.push {_isNew: true}

    $scope.remove = (course) ->
        $scope.courses.remove(course)

    $scope.editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/extraclasses.csv', $scope.encoding).then () ->
            $route.reload()

    $scope.numErrors = () ->
        return document.getElementsByClassName("has-error").length + document.getElementsByClassName("has-error-new").length > 0

    $scope.save = () ->
        if $scope.numErrors()
            $scope.first_save = true
            angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
            notify.error('Required data missing')
            return
        return $http.post("/api/lm/users/extra-courses?encoding=#{$scope.encoding}", $scope.courses).then () ->
            notify.success gettext('Saved')

    $scope.saveAndCheck = () ->
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/check.modal.html'
                controller: 'LMUsersCheckModalController'
                backdrop: 'static'
            )
    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/extraclasses.csv', $scope.encoding)
