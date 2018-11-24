angular.module('lmn.groupmembership').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/groupmembership',
        controller: 'LMNGroupMembershipController'
        templateUrl: '/lmn_groupmembership:resources/partial/index.html'


angular.module('lmn.groupmembership').controller 'LMNGroupMembershipController', ($scope, $http, $uibModal, gettext, notify, pageTitle, messagebox) ->
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

        project:
            typename: gettext('Projects')
            checkbox: true
            type: 'project'
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
       pageSize: 20

    $scope.isActive = (group) ->
        if  group.type is 'printergroup'
            if $scope.types.printergroup.checkbox is true
                return true
        if  group.type is 'schoolclass'
            if $scope.types.schoolclass.checkbox is true
                return true
        if  group.type is 'project'
            if $scope.types.schoolclass.checkbox is true
                return true
        return false

    $scope.resetClass = () ->
       # reset html class back (remove changed) so its not highlighted anymore
       result = document.getElementsByClassName("changed")
       while result.length
          result[0].className = result[0].className.replace( /(?:^|\s)changed(?!\S)/g , '' )
       # reset $scope.group attribute back not not changed so an additional enroll will not set these groups again
       for group in $scope.groups
           group['changed']= false
       return


    $scope.groupChanged = (groupIndex, item) ->
        # set $scope.group attribute
        # if changes made on page > 1 add this offsed to the index to change the right element in group list
        # TODO: BUG this is not working correctly if groups and printers are mixed up
        if $scope.paging.page > 1
            offSet = ($scope.paging.page - 1 ) * $scope.paging.pageSize
            groupIndex += offSet
        $scope.groups[groupIndex]['changed'] = true
        # set html class
        if document.getElementById(item).className.match (/(?:^|\s)changed(?!\S)/)
           document.getElementById(item).className = document.getElementById(item).className.replace( /(?:^|\s)changed(?!\S)/g , '' )
        else
           document.getElementById(item).className += " changed"

    $scope.getGroups = (username) ->
        $http.post('/api/lmn/groupmembership', {action: 'list-groups', username: username}).then (resp) ->
            $scope.groups = resp.data

    $scope.setGroups = (groups) ->
        $http.post('/api/lmn/groupmembership', {action: 'set-groups', username:$scope.identity.user, groups: groups}).then (resp) ->
            if resp['data'][0] == 'ERROR'
                notify.error (resp['data'][1])
            if resp['data'][0] == 'LOG'
                notify.success gettext(resp['data'][1])
                $scope.resetClass()
            if resp.data == 0
                notify.success gettext("Nothing changed")

    $scope.createProject = () ->
        messagebox.prompt(gettext('Project Name'), '').then (msg) ->
            if not msg.value
                return
            $http.post('/api/lmn/groupmembership', {action: 'create-project', username:$scope.identity.user, project: msg.value}).then (resp) ->
                notify.success gettext('Project Created')


    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
           return
        if $scope.identity.user is null
           return
        if $scope.identity.user is 'root'
           $scope.identity.user = 'hulk'
           # return
        $scope.getGroups($scope.identity.user)
        return
