angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/print-passwords',
        controller: 'LMUsersPrintPasswordsController'
        templateUrl: '/lm_users:resources/partial/print-passwords.html'


angular.module('lm.users').controller 'LMUsersPrintPasswordsOptionsModalController', ($scope, $uibModalInstance, $http, messagebox, gettext, recentIndex, recents) ->
    $scope.options = {
        format: 'pdf'
        one_per_page: false
        recent: recentIndex
    }
    $scope.title = if recentIndex != null then gettext("Recently added") + ": #{recents[recentIndex]}" else gettext('All users')

    $scope.print = () ->
        msg = messagebox.show(progress: true)
        $http.post('/api/lm/users/print', $scope.options).then (resp) ->
            location.href = "/api/lm/users/print-download/#{if recentIndex != null then 'add' else 'all'}.#{if $scope.options.format == 'pdf' then 'pdf' else 'csv'}"
            $uibModalInstance.close()
        .finally () ->
            msg.close()

    $scope.cancel = () ->
        $uibModalInstance.dismiss()


angular.module('lm.users').controller 'LMUsersPrintPasswordsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor) ->
    pageTitle.set(gettext('Print Passwords'))

    $http.get('/api/lm/users/print').then (resp) ->
        $scope.recents = resp.data

    $scope.select = (recentIndex) ->
        $uibModal.open(
            templateUrl: '/lm_users:resources/partial/print-passwords.options.modal.html'
            controller: 'LMUsersPrintPasswordsOptionsModalController'
            resolve:
                recentIndex: () -> recentIndex
                recents: () -> $scope.recents
        )
