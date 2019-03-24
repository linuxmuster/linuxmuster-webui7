angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/students-list',
        controller: 'LMUsersStudentsListController'
        templateUrl: '/lmn_users:resources/partial/students-list.html'


angular.module('lm.users').controller 'LMUsersStudentsListController', ($scope, $http, $location, $route, $uibModal, gettext, notify, lmEncodingMap, messagebox, pageTitle, lmFileEditor, lmFileBackups, filesystem) ->
    pageTitle.set(gettext('Students'))

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
            name: gettext('Student ID')
            fx: (x) -> x.id
        }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
        page: 1
        pageSize: 100

    $scope.add = () ->
        if $scope.students.length > 0
            $scope.paging.page = Math.floor(($scope.students.length - 1) / $scope.paging.pageSize) + 1
        $scope.filter = ''
        $scope.students.push { _isNew: true}

    $http.get('/api/lm/schoolsettings').then (resp) ->
        school = 'default-school'
        $scope.encoding = resp.data["userfile.students.csv"].encoding
        if $scope.encoding is 'auto'
            $http.post('/api/lmn/schoolsettings/determine-encoding', {path: '/etc/linuxmuster/sophomorix/'+school+'/students.csv'}).then (response) ->
                $scope.encoding = response.data
        $http.get("/api/lm/users/students-list?encoding=#{$scope.encoding}").then (resp) ->
            $scope.students = resp.data

    $scope.remove = (student) ->
        $scope.students.remove(student)

    $scope.editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/students.csv', $scope.encoding).then () ->
            $route.reload()

    $scope.save = () ->
        informationMissing = false
        for student in $scope.students
            if student['_isNew'] is true
                console.log (student)
                fields = ["class","last_name","first_name","birthday","id"]
                i = 0
                while i < fields.length
                  field = fields[i]
                  if not student.hasOwnProperty(field)
                    informationMissing = true
                  i++
        if informationMissing is true
            # TODO: Color line with missing info
            notify.error gettext('Empty field(s) in a row')
            return
        return $http.post("/api/lm/users/students-list?encoding=#{$scope.encoding}", $scope.students).then () ->
            notify.success gettext('Saved')

    $scope.saveAndCheck = () ->
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/check.modal.html'
                controller: 'LMUsersCheckModalController'
                backdrop: 'static'
            )

    $scope.confirmUpload = () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/upload.modal.html'
                controller: 'LMUsersUploadModalController'
                backdrop: 'static'
                resolve:
                    userlist: () -> 'students.csv'
            )

    $scope.backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/students.csv', $scope.encoding)

