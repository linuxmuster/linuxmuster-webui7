angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/extra-courses',
        controller: 'LMUsersExtraCoursesController'
        templateUrl: '/lm_users:resources/partial/extra-courses.html'


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

    $scope.add = () ->
        if $scope.courses.length > 0
            $scope.paging.page = Math.floor(($scope.courses.length - 1) / $scope.paging.pageSize) + 1
        $scope.courses.push {_isNew: true}

    $scope.remove = (course) ->
        $scope.courses.remove(course)

    $scope.editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/extraclasses.csv', $scope.encoding).then () ->
            $route.reload()

    $scope.save = () ->
        return $http.post("/api/lm/users/extra-courses?encoding=#{$scope.encoding}", $scope.courses).then () ->
            notify.success gettext('Saved')

    $scope.saveAndCheck = () ->
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lm_users:resources/partial/check.modal.html'
                controller: 'LMUsersCheckModalController'
                backdrop: 'static'
            )
    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/extraclasses.csv', $scope.encoding)
