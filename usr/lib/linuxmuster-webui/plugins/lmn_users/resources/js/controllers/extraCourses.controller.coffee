angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/users/extra-courses',
        controller: 'LMUsersExtraCoursesController'
        templateUrl: '/lmn_users:resources/partial/extra-courses.html'


angular.module('lmn.users').controller 'LMUsersExtraCoursesController', ($scope, $http, $uibModal, $route, notify, gettext, pageTitle, lmEncodingMap, lmFileEditor, lmFileBackups, validation) ->
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

    $http.get('/api/lmn/schoolsettings').then (resp) ->
        $scope.encoding = lmEncodingMap[resp.data.encoding_courses_extra] or 'ISO8859-1'
        $http.get("/api/lmn/users/lists/extraclasses?encoding=#{$scope.encoding}").then (resp) ->
            $scope.courses = resp.data

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
        if valid
            return ""
        if isnew and !$scope.first_save
            return "has-error-new"
        else
            return "has-error"

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
        return $http.post("/api/lmn/users/lists/extraclasses?encoding=#{$scope.encoding}", $scope.courses).then () ->
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
