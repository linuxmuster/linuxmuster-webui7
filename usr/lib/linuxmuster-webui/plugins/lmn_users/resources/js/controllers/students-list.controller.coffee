angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/students-list',
        controller: 'LMUsersStudentsListController'
        templateUrl: '/lmn_users:resources/partial/students-list.html'


angular.module('lm.users').controller 'LMUsersStudentsListController', ($scope, $http, $location, $route, $uibModal, gettext, notify, lmEncodingMap, messagebox, pageTitle, lmFileEditor, lmFileBackups, filesystem, validation) ->
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

    $scope.fields = {
       class:
          visible: true
          name: gettext('Class')
       last_name:
          visible: true
          name: gettext('Last Name')
       first_name:
          visible: true
          name: gettext('First Name')
       birthday:
          visible: true
          name: gettext('Birthday')
       id:
          visible: false
          name: gettext('Student ID')
    }

    $scope.first_save = false

    $scope.validateField = (name, val, isnew, filter=null) ->
        # TODO : what valid chars for class, name and course ?
        # Temporary solution : not filter these fields
        if name == 'TODO'
            return ""
            
        valid = validation["isValid"+name](val) && val
        
        if valid
            return ""
        if isnew and !$scope.first_save
            return "has-error-new"
        else
            return "has-error"

    $scope.add = () ->
        if $scope.students.length > 0
            $scope.paging.page = Math.floor(($scope.students.length - 1) / $scope.paging.pageSize) + 1
        $scope.filter = ''
        $scope.students.push { '_isNew': true, 'first_name': '', 'last_name': '', 'class': ''}

    $http.get('/api/lm/schoolsettings').then (resp) ->
        school = 'default-school'
        $scope.encoding = resp.data["userfile.students.csv"].encoding
        if $scope.encoding is 'auto'
            $http.post('/api/lmn/schoolsettings/determine-encoding', {path: '/etc/linuxmuster/sophomorix/'+school+'/students.csv'}).then (response) ->
                if response.data is 'unknown'
                    $scope.encoding = 'utf-8'
                else
                    $scope.encoding = response.data
        $http.get("/api/lm/users/students-list?encoding=#{$scope.encoding}").then (resp) ->
            $scope.students = resp.data

    $scope.remove = (student) ->
        $scope.students.remove(student)

    $scope.editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/students.csv', $scope.encoding).then () ->
            $route.reload()

    $scope.numErrors = () ->
        return document.getElementsByClassName("has-error").length + document.getElementsByClassName("has-error-new").length > 0

    $scope.save = () ->
        if $scope.numErrors()
            $scope.first_save = true
            angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
            notify.error('Required data missing')
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

