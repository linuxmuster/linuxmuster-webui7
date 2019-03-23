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

    $scope.save = () ->
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
