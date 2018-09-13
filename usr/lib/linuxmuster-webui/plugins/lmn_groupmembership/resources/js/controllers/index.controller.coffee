angular.module('lmn.groupmembership').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/groupmembership',
        controller: 'LMNGroupMembershipController'
        templateUrl: '/lmn_groupmembership:resources/partial/index.html'


angular.module('lmn.groupmembership').controller 'LMNGroupMembershipController', ($scope, $http, $uibModal, gettext, notify, pageTitle) ->
    pageTitle.set(gettext('Settings'))

    $scope.sorts = [
        {
            name: gettext('Class')
            fx: (x) -> x.classname
        }
        {
            name: gettext('Membership')
            fx: (x) -> x.membership
        }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
       page: 1
       pageSize: 50


    $scope.getGroups = (username) ->
        $http.post('/api/lmn/groupmembership', {action: 'list-groups', username: username}).then (resp) ->
            $scope.groups = resp.data

    $scope.setGroups = (groups) ->
        $http.post('/api/lmn/groupmembership', {action: 'set-groups', username:$scope.identity.user, groups: groups}).then (resp) ->
            notify.success gettext('Classes enrolled')

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
           return
        if $scope.identity.user is null
           return
        if $scope.identity.user is 'root'
           return
        $scope.getGroups($scope.identity.user)
        return
