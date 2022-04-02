angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/listmanagement',
       controller: 'LMUsersListManagementController'
       templateUrl: '/lmn_users:resources/partial/listmanagement.html'



angular.module('lmn.users').controller 'LMUsersListManagementController', ($scope, $http, $location, $route, $uibModal, gettext, hotkeys, notify, lmEncodingMap, messagebox, pageTitle, lmFileEditor, lmFileBackups, filesystem, validation) ->
    pageTitle.set(gettext('Listmanagement'))

    $scope.activeTab = 0
    $scope.tabs = ['students', 'teachers', 'extrastudents']

    lmn_get_school_configpath = (school) -> 
        #"This is an example of a function"
        if school == "default-school"
            return '/etc/linuxmuster/sophomorix/default-school/'
        else
            return '/etc/linuxmuster/sophomorix/'+school+'/'+school+'.'

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

    $scope.paging = {
        page_students: 1,
        page_teachers:1,
        page_extrastudents:1,
        page_courses:1,
        pageSize: 50
        }

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
            $scope.paging.page_students = Math.floor(($scope.students.length - 1) / $scope.paging.pageSize) + 1
        $scope.students_filter = ''
        $scope.students.push { '_isNew': true, 'first_name': '', 'last_name': '', 'class': ''}

    $scope.teachers_add = () ->
        if $scope.teachers.length > 0
                $scope.paging.page_teachers = Math.floor(($scope.teachers.length - 1) / $scope.paging.pageSize) + 1
            $scope.teachers_filter = ''
            $scope.teachers.push {class: 'Lehrer', _isNew: true}

    $scope.extrastudents_add = () ->
       if $scope.extrastudents.length > 0
          $scope.paging.page_extrastudents = Math.floor(($scope.extrastudents.length - 1) / $scope.paging.pageSize) + 1
       $scope.extrastudents_filter = ''
       $scope.extrastudents.push {_isNew: true}

    $scope.courses_add = () ->
        if $scope.courses.length > 0
            $scope.paging.page_courses = Math.floor(($scope.courses.length - 1) / $scope.paging.pageSize) + 1
        $scope.courses_filter = ''
        $scope.courses.push {_isNew: true}

    $scope.cleanupEmptyRow = (index, tab) ->
        # Cleanup removed empty cells from $scope.emptyCells
        index = ($scope.paging["page_"+tab]-1)*$scope.paging.pageSize+1+parseInt(index,10)
        for key of $scope.emptyCells
            if key.endsWith('-'+index)
                delete $scope.emptyCells[key]

    $scope.students_remove = (student, index) ->
        if student._isNew
            $scope.cleanupEmptyRow(index, "students")
        $scope.students.remove(student)

    $scope.teachers_remove= (teacher, index) ->
        if teacher._isNew
            $scope.cleanupEmptyRow(index, "teachers")
        $scope.teachers.remove(teacher)

    $scope.extrastudents_remove = (student, index) ->
        if student._isNew
            $scope.cleanupEmptyRow(index, "extrastudents")
        $scope.extrastudents.remove(student)

    $scope.courses_remove = (course, index) ->
        if course._isNew
            $scope.cleanupEmptyRow(index, "courses")
        $scope.courses.remove(course)

    $scope.getstudents = () ->
        if !$scope.students
            $http.get("/api/lm/users/students-list").then (resp) ->
                $scope.students = resp.data


    $scope.getteachers = () ->
        if !$scope.teachers
            $http.get("/api/lm/users/teachers-list").then (resp) ->
                $scope.teachers = resp.data


    $scope.getextrastudents = () ->
        if !$scope.extrastudents
            $http.get("/api/lm/users/extra-students").then (resp) ->
                    $scope.extrastudents = resp.data

    $scope.getcourses = () ->
        if !$scope.courses
            $http.get('/api/lm/schoolsettings').then (resp) ->
                $scope.courses_encoding = lmEncodingMap[resp.data.encoding_courses_extra] or 'ISO8859-1'
                $http.get("/api/lm/users/extra-courses?encoding=#{$scope.courses_encoding}").then (resp) ->
                    $scope.courses = resp.data



    $scope.students_editCSV = () ->
        path = lmn_get_school_configpath($scope.identity.profile.activeSchool)+'students.csv'
        lmFileEditor.show(path, $scope.students_encoding).then () ->
            $route.reload()

    $scope.teachers_editCSV = () ->
        path = lmn_get_school_configpath($scope.identity.profile.activeSchool)+'teachers.csv'
        lmFileEditor.show(path, $scope.teachers_encoding).then () ->
            $route.reload()


    $scope.extrastudents_editCSV = () ->
        path = lmn_get_school_configpath($scope.identity.profile.activeSchool)+'extrastudents.csv'
        lmFileEditor.show(path, $scope.extrastudents_encoding).then () ->
            $route.reload()

    $scope.courses_editCSV = () ->
        path = lmn_get_school_configpath($scope.identity.profile.activeSchool)+'extraclasses.csv'
        lmFileEditor.show(path, $scope.courses_encoding).then () ->
            $route.reload()


    $scope.students_save = () ->
        if $scope.numErrors()
            $scope.students_first_save = true
            $scope.show_errors = true
            angular.element(document.getElementsByClassName("has-error-new")).addClass('has-error')
            notify.error(gettext('Please check the errors.'))
            return
        $scope.show_errors = false
        $scope.students_first_save = false
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
        $scope.teachers_first_save = false
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
        $scope.extrastudents_first_save = false
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
        $scope.courses_first_save = false
        return $http.post("/api/lm/users/extra-courses?encoding=#{$scope.courses_encoding}", $scope.courses).then () ->
           notify.success gettext('Saved')

    $scope.confirmUpload = (type, role) ->
        if (type == "custom")
            templateUrl = '/lmn_users:resources/partial/uploadcustom.modal.html'
            controller = 'LMUsersUploadCustomModalController'
        else
            templateUrl = '/lmn_users:resources/partial/upload.modal.html'
            controller = 'LMUsersUploadModalController'

        $uibModal.open(
            templateUrl: templateUrl
            controller: controller
            backdrop: 'static'
            resolve:
                userlist: () -> role + '.csv'
        )

    $scope.students_backups = () ->
        path = lmn_get_school_configpath($scope.identity.profile.activeSchool)+'students.csv'
        lmFileBackups.show(path, $scope.students_encoding)

    $scope.teachers_backups = () ->
        path = lmn_get_school_configpath($scope.identity.profile.activeSchool)+'teachers.csv'
        lmFileBackups.show(path, $scope.teachers_encoding)

    $scope.extrastudents_backups = () ->
        path = lmn_get_school_configpath($scope.identity.profile.activeSchool)+'extrastudents.csv'
        lmFileBackups.show(path, $scope.extrastudents_encoding)

    $scope.courses_backups = () ->
        path = lmn_get_school_configpath($scope.identity.profile.activeSchool)+'extraclasses.csv'
        lmFileBackups.show(path, $scope.courses_encoding)

    # general functions

    $scope.error_msg = {}
    $scope.show_errors = false
    $scope.emptyCells = {}

    $scope.dictLen = (d) ->
        return Object.keys(d).length

    $scope.validateField = (name, val, isnew, ev, tab, filter=null) ->
        # TODO : what valid chars for class, name and course ?
        # Temporary solution : not filter these fields

        if $scope[tab+"_first_save"]
            errorClass = "has-error-new has-error"
        else
            errorClass = "has-error-new"
        ev = ($scope.paging["page_"+tab]-1)*$scope.paging.pageSize+1+parseInt(ev,10)
        if name.startsWith('TODO')
            if !val
                $scope.emptyCells[name+"-"+tab+"-"+ev] = 1
                return errorClass
            else
                delete $scope.emptyCells[name+"-"+tab+"-"+ev]
                return ""

        # TODO : is pasword necessary for extra course ? Filtered only if not undefined.
        # Desired passwords will be marked if not strong enough, is it necessary for extra courses ?
        if name == 'Password' and !val
            return ""

        test = validation["isValid"+name](val)

        # Ensure the login is not duplicated, but ignore empty login
        if filter == 'teachers'
            if val != ''
                test = test && ($scope.teachers.filter(validation.findval('login', val)).length < 2)
        else if filter == 'extrastudents'
            if val != ''
                test = test && ($scope.extrastudents.filter(validation.findval('login', val)).length < 2)

        # Login for teachers may be empty
        if name == 'Login' and ( filter == 'teachers' or filter == 'extrastudents' ) and test == true
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

        return errorClass

    $scope.numErrors = () ->
        angular.element(document.getElementsByClassName("has-error")).removeClass('has-error')
        return $scope.dictLen($scope.error_msg) + $scope.dictLen($scope.emptyCells) > 0

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

    # pulling active school from backend
    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
           return
        if $scope.identity.user is null
           return
        if $scope.identity.user is 'root'
           return
        
        $http.get("/api/lmn/activeschool").then (resp) ->
            $scope.identity.profile.activeSchool = resp.data

    # Loading first tab
    $scope.getstudents()

    hotkeys.on $scope, (key, event) ->
        current_tab = $scope.tabs[$scope.activeTab]
        if (key == 'I' && event.ctrlKey)
            $scope.saveAndCheck(current_tab)
            return true

        if (key == 'S' && event.ctrlKey)
            $scope[current_tab + "_save"]()
            return true

        if (key == 'B' && event.ctrlKey)
            $scope[current_tab + "_backups"]()
            return true

        return false
