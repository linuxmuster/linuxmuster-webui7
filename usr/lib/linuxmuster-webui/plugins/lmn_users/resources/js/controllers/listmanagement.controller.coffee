angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/listmanagement',
       controller: 'LMUsersListManagementController'
       templateUrl: '/lmn_users:resources/partial/listmanagement.html'


angular.module('lm.users').controller 'LMUsersListManagementController', ($scope, $http, $location, $route, $uibModal, gettext, notify, lmEncodingMap, messagebox, pageTitle, lmFileEditor, lmFileBackups, filesystem, validation) ->
    pageTitle.set(gettext('Listmanagement'))

    $scope.students_sorts = [
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

    $scope.teachers_sorts = [
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
          name: gettext('Login')
          fx: (x) -> x.login
       }
    ]

    $scope.extrastudents_sorts = [
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
    $scope.courses_sorts = [
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



    $scope.students_sort = $scope.students_sorts[0]
    $scope.teachers_sort = $scope.teachers_sorts[0]
    $scope.extrastudents_sort = $scope.students_sorts[0]
    $scope.courses_sort= $scope.teachers_sorts[0]

    $scope.paging =
        page: 1
       pageSize: 100

    $scope.students_fields = {
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

    $scope.teachers_fields = {
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

    $scope.extrastudents_fields = {
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
        login:
            visible: true
            name: gettext('Login')
    }


    $scope.teachers_first_save = false
    $scope.students_first_save = false
    $scope.extrastudents_first_save = false
    $scope.courses_first_save= false

    $scope.teachers = ''
    $scope.students = ''
    $scope.extrastudents = ''
    $scope.courses = ''

    $scope.students_add = () ->
        if $scope.students.length > 0
            $scope.paging.page = Math.floor(($scope.students.length - 1) / $scope.paging.pageSize) + 1
        $scope.students_filter = ''
        $scope.students.push { '_isNew': true, 'first_name': '', 'last_name': '', 'class': ''}

    $scope.teachers_add = () ->
        if $scope.teachers.length > 0
                $scope.paging.page = Math.floor(($scope.teachers.length - 1) / $scope.paging.pageSize) + 1
            $scope.teachers_filter = ''
            $scope.teachers.push {class: 'Lehrer', _isNew: true}

    $scope.extrastudents_add = () ->
       if $scope.extrastudents.length > 0
          $scope.paging.page = Math.floor(($scope.extrastudents.length - 1) / $scope.paging.pageSize) + 1
       $scope.extrastudents_filter = ''
       $scope.extrastudents.push {_isNew: true}

    $scope.courses_add = () ->
        if $scope.courses.length > 0
            $scope.paging.page = Math.floor(($scope.courses.length - 1) / $scope.paging.pageSize) + 1
        $scope.courses_filter = ''
        $scope.courses.push {_isNew: true}


    $scope.students_remove = (student) ->
        $scope.students.remove(student)

    $scope.teachers_remove= (teacher) ->
        $scope.teachers.remove(teacher)

    $scope.extrastudents_remove = (student) ->
       $scope.extrastudents.remove(student)

    $scope.courses_remove = (course) ->
       $scope.courses.remove(course)

    $scope.getstudents = () ->
        if !$scope.students
           $http.get('/api/lm/schoolsettings').then (resp) ->
               school = 'default-school'
               $scope.students_encoding = resp.data["userfile.students.csv"].encoding
               if $scope.students_encoding is 'auto'
                   $http.post('/api/lmn/schoolsettings/determine-encoding', {path: '/etc/linuxmuster/sophomorix/'+school+'/students.csv'}).then (response) ->
                     if response.data is 'unknown'
                         $scope.students_encoding = 'utf-8'
                     else
                         $scope.students_encoding = response.data
               $http.get("/api/lm/users/students-list?encoding=#{$scope.students_encoding}").then (resp) ->
                   $scope.students = resp.data

    $scope.getteachers = () ->
        if !$scope.teachers
           $http.get('/api/lm/schoolsettings').then (resp) ->
               school = 'default-school'
               $scope.teachers_encoding = resp.data["userfile.teachers.csv"].encoding
               if $scope.teachers_encoding is 'auto'
                  $http.post('/api/lmn/schoolsettings/determine-encoding', {path: '/etc/linuxmuster/sophomorix/'+school+'/teachers.csv'}).then (response) ->
                     if response.data is 'unknown'
                        $scope.teachers_encoding = 'utf-8'
                     else
                        $scope.teachers_encoding = response.data
               $http.get("/api/lm/users/teachers-list?encoding=#{$scope.students_encoding}").then (resp) ->
                    $scope.teachers = resp.data

    $scope.getextrastudents = () ->
        if !$scope.extrastudents
            $http.get('/api/lm/schoolsettings').then (resp) ->
                school = 'default-school'
                $scope.extrastudents_encoding = resp.data["userfile.extrastudents.csv"].encoding
                if $scope.extrastudents_encoding is 'auto'
                   $http.post('/api/lmn/schoolsettings/determine-encoding', {path: '/etc/linuxmuster/sophomorix/'+school+'/extrastudents.csv'}).then (response) ->
                      if response.data is 'unknown'
                         $scope.extrastudents_encoding = 'utf-8'
                      else
                         $scope.extrastudents_encoding = response.data
                $http.get("/api/lm/users/extra-students?encoding=#{$scope.extrastudents_encoding}").then (resp) ->
                    $scope.extrastudents = resp.data

    $scope.getcourses = () ->
        if !$scope.courses
            $http.get('/api/lm/schoolsettings').then (resp) ->
                $scope.courses_encoding = lmEncodingMap[resp.data.encoding_courses_extra] or 'ISO8859-1'
                $http.get("/api/lm/users/extra-courses?encoding=#{$scope.courses_encoding}").then (resp) ->
                    $scope.courses = resp.data



    $scope.students_editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/students.csv', $scope.students_encoding).then () ->
            $route.reload()

    $scope.teachers_editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/teachers.csv', $scope.students_encoding).then () ->
            $route.reload()

    $scope.extrastudents_editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/extrastudents.csv', $scope.extrastudents_encoding).then () ->
            $route.reload()

    $scope.courses_editCSV = () ->
        lmFileEditor.show('/etc/linuxmuster/sophomorix/default-school/extraclasses.csv', $scope.courses_encoding).then () ->
            $route.reload()


    $scope.students_save = () ->
        if $scope.numErrors()
            $scope.students_first_save = true
            $scope.show_errors = true
            angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
            notify.error(gettext('Please check the errors.'))
            return
        $scope.show_errors = false
        return $http.post("/api/lm/users/students-list?encoding=#{$scope.students_encoding}", $scope.students).then () ->
            notify.success gettext('Saved')

    $scope.teachers_save = () ->
        if $scope.numErrors()
           $scope.teachers_first_save = true
           $scope.show_errors = true
           angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
           notify.error(gettext('Please check the errors.'))
           return
        $scope.show_errors = false
        return $http.post("/api/lm/users/teachers-list?encoding=#{$scope.teachers_encoding}", $scope.teachers).then () ->
           notify.success gettext('Saved')

    $scope.extrastudents_save = () ->
        if $scope.numErrors()
           $scope.extrastudents_first_save = true
           $scope.show_errors = true
           angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
           notify.error(gettext('Please check the errors.'))
           return
        $scope.show_errors = false
        return $http.post("/api/lm/users/extra-students?encoding=#{$scope.extrastudents_encoding}", $scope.extrastudents).then () ->
           notify.success 'Saved'

    $scope.courses_save = () ->
        if $scope.numErrors()
           $scope.courses_first_save = true
           $scope.show_errors = true
           angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
           notify.error(gettext('Please check the errors.'))
           return
        $scope.show_errors = false
        return $http.post("/api/lm/users/extra-courses?encoding=#{$scope.courses_encoding}", $scope.courses).then () ->
           notify.success gettext('Saved')


    $scope.students_confirmUpload = () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/upload.modal.html'
                controller: 'LMUsersUploadModalController'
                backdrop: 'static'
                resolve:
                    userlist: () -> 'students.csv'
            )

    $scope.teachers_confirmUpload = () ->
            $uibModal.open(
               templateUrl: '/lmn_users:resources/partial/upload.modal.html'
               controller: 'LMUsersUploadModalController'
               backdrop: 'static'
               resolve:
                    userlist: () -> 'teachers.csv'
            )




    $scope.students_backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/students.csv', $scope.students_encoding)

    $scope.teachers_backups = () ->
        lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/teachers.csv', $scope.teachers_encoding)

    $scope.extrastudents_backups = () ->
       lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/extrastudents.csv', $scope.extrastudents_encoding)

    $scope.courses_backups = () ->
       lmFileBackups.show('/etc/linuxmuster/sophomorix/default-school/extraclasses.csv', $scope.courses_encoding)

    # general functions

    $scope.error_msg = {}
    $scope.show_errors = false
    $scope.emptyCells = {}

    $scope.dictLen = (d) ->
        return Object.keys(d).length

    $scope.validateField = (name, val, isnew, ev, tab, filter=null) ->
        # TODO : what valid chars for class, name and course ?
        # Temporary solution : not filter these fields
        if name.startsWith('TODO')
            if !val
                $scope.emptyCells[name+"-"+tab+"-"+ev] = 1
                return "has-error-new"
            else
                delete $scope.emptyCells[name+"-"+tab+"-"+ev]
                return ""

        # TODO : is pasword necessary for extra course ? Filtered only if not undefined.
        # Desired passwords will be marked if not strong enough, is it necessary for extra courses ?
        if name == 'Password' and !val
            return ""

        test = validation["isValid"+name](val)

        if filter == 'teachers'
            test = test && ($scope.teachers.filter(validation.findval('login', val)).length < 2)
        else if filter == 'extrastudents'
            test = test && ($scope.extrastudents.filter(validation.findval('login', val)).length < 2)

        # Login for teachers may be empty
        if name == 'Login' and filter == 'teachers' and test == true
            delete $scope.error_msg[name+"-"+tab+"-"+ev]
            delete $scope.emptyCells[name+"-"+tab+"-"+ev]
            return ""
        else if test == true && val
            delete $scope.error_msg[name+"-"+tab+"-"+ev]
            delete $scope.emptyCells[name+"-"+tab+"-"+ev]
            return ""
        else if !val
            delete $scope.error_msg[name+"-"+tab+"-"+ev]
            $scope.emptyCells[name+"-"+tab+"-"+ev] = 1
        else
            delete $scope.emptyCells[name+"-"+tab+"-"+ev]
            if Object.values($scope.error_msg).indexOf(gettext(tab) + ": " + test) == -1
                $scope.error_msg[name+"-"+tab+"-"+ev] = gettext(tab) + ": " + test

        return "has-error-new"

    $scope.numErrors = () ->
        angular.element(document.getElementsByClassName("has-error")).removeClass('has-error')
        return document.getElementsByClassName("has-error-new").length > 0

    $scope.saveAndCheck = (name) ->
        if $scope.numErrors()
            $scope[name+"_first_save"] = true
            $scope.show_errors = true
            angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
            notify.error(gettext('Please check the errors.'))
            return
        $scope.show_errors = false
        $scope[name+"_save"]().then () ->
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/check.modal.html'
                controller: 'LMUsersCheckModalController'
                backdrop: 'static'
            )

    # TODO: Add paging
    # Loading first tab
    $scope.getstudents()
