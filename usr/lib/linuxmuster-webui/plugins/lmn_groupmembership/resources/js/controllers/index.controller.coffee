angular.module('lmn.groupmembership').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/groupmembership',
        controller: 'LMNGroupMembershipController'
        templateUrl: '/lmn_groupmembership:resources/partial/index.html'


angular.module('lmn.groupmembership').controller 'LMNGroupMembershipController', ($scope, $http, $uibModal, gettext, notify, pageTitle, lmFileBackups) ->
    pageTitle.set(gettext('Settings'))


    $http.get('/api/lmn/groupmembership').then (resp) ->
        school = 'default-school'
        console.log(resp.data)
        $scope.groups = resp.data
