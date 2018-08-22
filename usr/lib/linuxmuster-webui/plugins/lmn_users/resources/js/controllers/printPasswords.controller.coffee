angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/print-passwords',
        controller: 'LMUsersPrintPasswordsController'
        templateUrl: '/lm_users:resources/partial/print-passwords.html'


angular.module('lm.users').controller 'LMUsersPrintPasswordsOptionsModalController', ($scope, $uibModalInstance, $http, messagebox, gettext, schoolclass, classes, user) ->
    $scope.options = {
        format: 'pdf'
        one_per_page: false
        schoolclass: schoolclass
        user: user
    }
    if $scope.options.user is 'root'
        $scope.options.user = 'global-admin'

    $scope.title = if schoolclass != null then gettext("Class") + ": #{classes[class]}" else gettext('All users')

    $scope.print = () ->
        msg = messagebox.show(progress: true)
        $http.post('/api/lm/users/print', $scope.options).then (resp) ->
            location.href = "/api/lm/users/print-download/#{if schoolclass != null then schoolclass else 'add'}-#{$scope.options.user}.#{if $scope.options.format == 'pdf' then 'pdf' else 'csv'}"
            $uibModalInstance.close()
        .finally () ->
            msg.close()

    $scope.cancel = () ->
        $uibModalInstance.dismiss()


angular.module('lm.users').controller 'LMUsersPrintPasswordsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor) ->
    pageTitle.set(gettext('Print Passwords'))

    $http.get('/api/lm/users/print').then (resp) ->
        $scope.classes = resp.data
        console.log ($scope.classes)

    $scope.select = (schoolclass,user) ->
        $uibModal.open(
            templateUrl: '/lm_users:resources/partial/print-passwords.options.modal.html'
            controller: 'LMUsersPrintPasswordsOptionsModalController'
            resolve:
                schoolclass: () -> schoolclass
                classes: () -> $scope.classes
                user: () -> user
        )
