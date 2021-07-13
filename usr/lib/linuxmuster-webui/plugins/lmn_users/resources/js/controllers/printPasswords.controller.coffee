angular.module('lmn.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/print-passwords',
        controller: 'LMUsersPrintPasswordsController'
        templateUrl: '/lmn_users:resources/partial/print-passwords.html'


angular.module('lmn.users').controller 'LMUsersPrintPasswordsOptionsModalController', ($scope, $uibModalInstance, $http, notify, messagebox, gettext, schoolclass, user) ->
    $scope.options = {
        format: 'pdf'
        one_per_page: false
        pdflatex: false
        schoolclass: schoolclass
        user: user
    }

    if $scope.options.user is 'root'
        $scope.options.user = 'global-admin'

    $scope.title = if schoolclass != '' then gettext("Class") + ": #{schoolclass.join(',')}" else gettext('All users '+$scope.identity.profile.activeSchool)

    $scope.print = () ->
        msg = messagebox.show(progress: true)
        $http.post('/api/lm/users/print', $scope.options).then (resp) ->
            if resp.data == 'success'
                notify.success(gettext("Created password pdf"))
                if schoolclass.length == 1
                    prefix = 'add'
                    if schoolclass[0]
                        prefix = schoolclass[0]
                else
                    prefix = 'multiclass'

                location.href = "/api/lm/users/print-download/#{prefix}-#{$scope.options.user}.#{$scope.options.format}"
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

    $scope.getGroups = (username) ->
        if $scope.identity.user == 'root' || $scope.identity.profile.sophomorixRole == 'globaladministrator' || $scope.identity.profile.sophomorixRole == 'schooladministrator'
            $http.get('/api/lm/users/get-classes').then (resp) ->
                $scope.classes = resp.data
        else
            $scope.classes = []
            for membership in $scope.identity.profile.memberOf
                if membership.indexOf("OU=Students") > -1
                    # Split "CN=10b,OU=10b,OU=Students,..."
                    classname = membership.split(',')[0].split('=')[1]
                    $scope.classes.push(classname)

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
            return
        if $scope.identity.user is null
            return
        if $scope.identity.user is 'root'
            return
        
        $http.get("/api/lmn/activeschool").then (resp) ->
            $scope.identity.profile.activeSchool = resp.data
            $scope.getGroups($scope.identity.user)
            return
