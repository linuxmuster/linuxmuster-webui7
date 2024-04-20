angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/users/print-passwords',
        controller: 'LMUsersPrintPasswordsController'
        templateUrl: '/lmn_users:resources/partial/print-passwords.html'


angular.module('lmn.users').controller 'LMUsersPrintPasswordsOptionsModalController', ($scope, $uibModalInstance, $http, notify, messagebox, gettext, schoolclass, user, adminClass, customFields) ->
    $scope.options = {
        format: 'pdf'
        one_per_page: false
        pdflatex: false
        schoolclass: schoolclass
        user: user
        adminClass: adminClass
        template_one_per_page: ''
        template_multiple: ''
    }

    if $scope.options.user is 'root'
        $scope.options.user = 'global-admin'

    if $scope.options.adminClass.includes('admins')
        $http.get('/api/lmn/schoolsettings/latex-templates').then (rp) ->
            $scope.templates_individual = rp.data[0]
            $scope.templates_multiple = rp.data[1]
            $scope.options['template_one_per_page'] = $scope.templates_individual[0]
            $scope.options['template_multiple'] = $scope.templates_multiple[0]

            customFields.load_config().then (resp) ->
                $scope.passwordTemplates = resp.passwordTemplates

                for template in $scope.templates_individual
                    if template.path == $scope.passwordTemplates.individual
                        $scope.options['template_one_per_page'] = template
                        break

                for template in $scope.templates_multiple
                    if template.path == $scope.passwordTemplates.multiple
                        $scope.options['template_multiple'] = template
                        break

    $scope.title = if schoolclass != '' then gettext("Class") + ": #{schoolclass.join(',')}" else gettext('All users '+$scope.identity.profile.activeSchool)

    $scope.print = () ->
        msg = messagebox.show(progress: true)
        $http.post('/api/lmn/users/print', $scope.options).then (resp) ->
            if resp.data == 'success'
                notify.success(gettext("Created password pdf"))
                if schoolclass.length == 1
                    prefix = 'add'
                    if schoolclass[0]
                        prefix = schoolclass[0]
                else
                    prefix = 'multiclass'

                location.href = "/api/lmn/users/passwords/download/#{prefix}-#{$scope.options.user}.#{$scope.options.format}"
            else
                notify.error(gettext("Could not create password pdf"))
            $uibModalInstance.close()
        .finally () ->
            msg.close()

    $scope.cancel = () ->
        $uibModalInstance.dismiss()


angular.module('lmn.users').controller 'LMUsersPrintPasswordsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor) ->
    pageTitle.set(gettext('Print Passwords'))

    $scope.launch_print_modal = (schoolclass) ->
        if "" in $scope.selection and $scope.selection.length > 1
            notify.warning(gettext("It's not possible to print all users and a class at the same time."))
            return
        $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/print-passwords.options.modal.html'
            controller: 'LMUsersPrintPasswordsOptionsModalController'
            resolve:
                schoolclass: () -> schoolclass
                user: () -> $scope.identity.user
                adminClass: () -> $scope.adminClass
        )

    $scope.selection = []

    $scope.select = (schoolclass) ->
        position = $scope.selection.indexOf(schoolclass)
        if position > -1
            $scope.selection.splice(position, 1)
        else
            $scope.selection.push(schoolclass)
        if "" in $scope.selection and $scope.selection.length > 1
            notify.warning(gettext("It's not possible to print all users and a class at the same time."))

    $scope.sort_schoolclasses = (schoolclasses) ->
        schoolclasses.sort((a,b) ->
            anum = parseInt(a, 10)
            bnum = parseInt(b, 10)
            if (anum > bnum)
                return 1
            if (anum < bnum)
                return -1
            return 0
        )
        return schoolclasses

    $scope.getGroups = (username) ->
        if $scope.identity.user == 'root' || $scope.identity.profile.sophomorixRole == 'globaladministrator' || $scope.identity.profile.sophomorixRole == 'schooladministrator'
            $http.get('/api/lmn/users/classes').then (resp) ->
                $scope.classes = $scope.sort_schoolclasses(resp.data)
                $scope.admin_warning = true
        else
            $scope.admin_warning = false
            $scope.classes = []
            for membership in $scope.identity.profile.memberOf
                if membership.indexOf("OU=Students") > -1
                    # Split "CN=10b,OU=10b,OU=Students,..."
                    classname = membership.split(',')[0].split('=')[1]
                    $scope.classes.push(classname)
            $scope.classes = $scope.sort_schoolclasses($scope.classes)

    $scope.printCSV = (schoolclass) ->
        msg = messagebox.show(progress: true)
        $http.post('/api/lmn/users/print_csv', {user: $scope.identity.user, schoolclass:schoolclass}).then (resp) ->
            if resp.data == 'success'
                notify.success(gettext("Created password csv"))
                location.href = "/api/lmn/users/passwords/download/#{schoolclass}-#{$scope.identity.user}.csv"
            else
                notify.error(gettext("Could not create password csv"))
        .finally () ->
            msg.close()

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
            return
        if $scope.identity.user is null
            return
        if $scope.identity.user is 'root'
            return

        $scope.adminClass = $scope.identity.profile.sophomorixAdminClass
        $http.get("/api/lmn/activeschool").then (resp) ->
            $scope.identity.profile.activeSchool = resp.data
            $scope.getGroups($scope.identity.user)
            return
