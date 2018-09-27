angular.module('lmn.groupmembership').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/groupmembership',
        controller: 'LMNGroupMembershipController'
        templateUrl: '/lmn_groupmembership:resources/partial/index.html'


angular.module('lmn.groupmembership').controller 'LMNGroupMembershipController', ($scope, $http, $uibModal, gettext, notify, pageTitle) ->
    pageTitle.set(gettext('Group Membership'))

    $scope.types = {
        schoolclass:
            typename: gettext('Schoolclass')
            checkbox: true
            type: 'schoolclass'

        printergroup:
            typename: gettext('Printer')
            checkbox: true
            type: 'printergroup'
    }

    $scope.sorts = [
        {
            name: gettext('Groupname')
            fx: (x) -> x.groupname
        }
        {
            name: gettext('Membership')
            fx: (x) -> x.membership
        }
        {
            name: gettext('Type')
            fx: (x) -> x.type
        }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
       page: 1
       pageSize: 50

    $scope.isActive = (group) ->
        if  group.type is 'printergroup'
            if $scope.types.printergroup.checkbox is true
                return true
        if  group.type is 'schoolclass'
            if $scope.types.schoolclass.checkbox is true
                return true
        return false

    $scope.resetClass = () ->
       result = document.getElementsByClassName("changed")
       while result.length
          result[0].className = result[0].className.replace( /(?:^|\s)changed(?!\S)/g , '' )
       return


    $scope.groupChanged = (groupIndex, item) ->
        console.log ($scope.groups[groupIndex])
        $scope.groups[groupIndex]['changed'] = true
        if document.getElementById(item).className.match (/(?:^|\s)changed(?!\S)/)
           document.getElementById(item).className = document.getElementById(item).className.replace( /(?:^|\s)changed(?!\S)/g , '' )
        else
           document.getElementById(item).className += " changed"

    $scope.getGroups = (username) ->
        $http.post('/api/lmn/groupmembership', {action: 'list-groups', username: username}).then (resp) ->
            $scope.groups = resp.data

    $scope.setGroups = (groups) ->
        $http.post('/api/lmn/groupmembership', {action: 'set-groups', username:$scope.identity.user, groups: groups}).then (resp) ->
            notify.success gettext('Classes enrolled')
            $scope.resetClass()

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
           return
        if $scope.identity.user is null
           return
        #if $scope.identity.user is 'root'
        #   return
        $scope.identity.user = 'hulk'
        $scope.getGroups($scope.identity.user)
        return
