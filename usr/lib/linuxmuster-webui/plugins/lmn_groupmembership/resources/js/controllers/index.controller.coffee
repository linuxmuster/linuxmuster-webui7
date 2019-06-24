isValidName = (name) ->
    regExp =  /^[a-z0-9]*$/i
    validName = regExp.test(name)
    return validName

angular.module('lmn.groupmembership').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/groupmembership',
        controller: 'LMNGroupMembershipController'
        templateUrl: '/lmn_groupmembership:resources/partial/index.html'

angular.module('lmn.groupmembership').controller 'LMNGroupDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, groupType, groupName) ->

        $scope.editGroupMembers = (groupName, groupDetails) ->
            $uibModal.open(
                templateUrl: '/lmn_groupmembership:resources/partial/editMembers.modal.html'
                controller:  'LMNGroupEditController'
                size: 'lg'
                resolve:
                   groupName: () -> groupName
                   groupDetails: () -> groupDetails
            ).result.then (result)->
                if result.response is 'refresh'
                    $scope.getGroupDetails ([groupType, groupName])

        $scope.showAdminDetails = true
        $scope.showMemberDetails = true

        $scope.killProject = (project) ->
             messagebox.show(text: "Do you really want to delete '#{project}'? This can't be undone!", positive: 'Delete', negative: 'Cancel').then () ->
                msg = messagebox.show(progress: true)
                $http.post('/api/lmn/groupmembership', {action: 'kill-project', username:$scope.identity.user, project: project}).then (resp) ->
                    #console.log (resp.data)
                    if resp['data'][0] == 'ERROR'
                        notify.error (resp['data'][1])
                    if resp['data'][0] == 'LOG'
                        notify.success gettext(resp['data'][1])
                        $uibModalInstance.close(response: 'refresh')
                .finally () ->
                    msg.close()

        $scope.formatDate = (date) ->
           return Date(date)

        $http.post('/api/lm/all-users').then (resp) ->
            $scope.allUsers = resp.data

        $scope.filterDNLogin = (dn) ->
            if dn.indexOf('=') != -1
                return dn.split(',')[0].split('=')[1]
            else
                return dn

        $scope.getGroupDetails = (group) ->
            groupType = group[0]
            groupName = group[1]
            $http.post('/api/lmn/groupmembership/details', {action: 'get-specified', groupType: groupType, groupName: groupName}).then (resp) ->
                $scope.groupName    = groupName
                $scope.groupDetails = resp.data
                $scope.members = [$scope.filterDNLogin(member) for member in resp.data[groupName]['member']]
                $scope.admins = [$scope.filterDNLogin(member) for member in resp.data[groupName]['sophomorixAdmins']]

        $scope.groupType = groupType
        $scope.getGroupDetails ([groupType, groupName])
        $scope.close = () ->
            $uibModalInstance.dismiss()

angular.module('lmn.groupmembership').controller 'LMNGroupEditController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, groupName, groupDetails) ->
        $scope.sorts = [
            {
                name: gettext('Given name')
                id: 'givenName'
                fx: (x) -> x.givenName
            }
            {
                name: gettext('Name')
                id: 'sn'
                fx: (x) -> x.sn
            }
            {
                name: gettext('Membership')
                id: 'membership'
                fx: (x) -> x.membership
            }
            #{
            #    name: gettext('Class')
            #    fx: (x) -> x.sophomorixAdminClass
            #}
        ]
        $scope.sort = $scope.sorts[1]
        console.log ($scope.sort)
        $scope.groupName = groupName
        $scope.sortReverse = false


        $scope.checkInverse = (sort ,currentSort) ->
            if sort == currentSort
                $scope.sortReverse = !$scope.sortReverse
            else
                $scope.sortReverse = false



        $scope.setMembers = (students, teachers) ->
            msg = messagebox.show(progress: true)
            members = students.concat(teachers)
            $http.post('/api/lmn/groupmembership/details', {action: 'set-members', username:$scope.identity.user, members: members, groupName: groupName}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                    $uibModalInstance.close(response: 'refresh')
                    #$scope.resetClass()
            .finally () ->
                msg.close()

        groupDN = groupDetails[groupName]['dn']
        $http.post('/api/lm/sophomorixUsers/students', {action: 'get-all'}).then (resp) ->
            students = resp.data
            $scope.students = students
            console.log (students)
            classes = []
            for student in students
                if student['sophomorixAdminClass'] not in classes
                    classes.push student['sophomorixAdminClass']
                if groupDN in student['memberOf']
                    student['membership'] = true
                else
                    student['membership'] = false
            $scope.classes = classes
            console.log ($scope.classes)
            ## TODO : add class ?
            ## TODO : add other project members ?
            ## TODO : add projectadmin
        $http.post('/api/lm/sophomorixUsers/teachers', {action: 'get-list'}).then (resp) ->
            teachers = resp.data
            $scope.teachers = teachers
            console.log (teachers)
            for teacher in teachers
                if groupDN in teacher['memberOf']
                    teacher['membership'] = true
                else
                    teacher['membership'] = false

        $scope.close = () ->
            $uibModalInstance.dismiss()

angular.module('lmn.groupmembership').controller 'LMNGroupMembershipController', ($scope, $http, $uibModal, gettext, notify, pageTitle, messagebox) ->
    pageTitle.set(gettext('Group Membership'))

    $scope.types = {
        schoolclass:
            typename: gettext('Schoolclass')
            name: gettext('Groupname')
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
    ]
    $scope.sort = $scope.sorts[0]
    $scope.sortReverse= false
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

    $scope.checkInverse = (sort ,currentSort) ->
        if sort == currentSort
            $scope.sortReverse = !$scope.sortReverse
        else
            $scope.sortReverse = false

    $scope.resetClass = () ->
       # reset html class back (remove changed) so its not highlighted anymore
       result = document.getElementsByClassName("changed")
       while result.length
          result[0].className = result[0].className.replace( /(?:^|\s)changed(?!\S)/g , '' )
       # reset $scope.group attribute back not not changed so an additional enroll will not set these groups again
       for group in $scope.groups
           group['changed']= false
       return


    $scope.groupChanged = (item) ->
        for group in $scope.groups
            if group['groupname'] == item
                if group['changed'] == false
                    group['changed'] = true
                else
                    group['changed'] = false
        # set html class
        if document.getElementById(item).className.match (/(?:^|\s)changed(?!\S)/)
           document.getElementById(item).className = document.getElementById(item).className.replace( /(?:^|\s)changed(?!\S)/g , '' )
        else
           document.getElementById(item).className += " changed"

    $scope.getGroups = (username) ->
        $http.post('/api/lmn/groupmembership', {action: 'list-groups', username: username}).then (resp) ->
            $scope.groups = resp.data
            schoolclassCount = 0
            printergroupCount = 0
            projectCount = 0
            for group in $scope.groups
                if group.type == 'schoolclass'
                    schoolclassCount = schoolclassCount + 1
            for group in $scope.groups
                if group.type == 'printergroup'
                    printergroupCount = printergroupCount + 1
            for group in $scope.groups
                if group.type == 'project'
                    projectCount = projectCount + 1
            $scope.schoolclassCount= schoolclassCount
            $scope.printergroupCount = printergroupCount
            $scope.projectCount = projectCount


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
            if not isValidName(msg.value)
                notify.error gettext('Not a valid name! Only alphanumeric characters are allowed!')
                return
            $http.post('/api/lmn/groupmembership', {action: 'create-project', username:$scope.identity.user, project: msg.value}).then (resp) ->
                notify.success gettext('Project Created')
                $scope.getGroups ($scope.identity.user)

    $scope.showGroupDetails = (index, groupType, groupName) ->
        $uibModal.open(
            templateUrl: '/lmn_groupmembership:resources/partial/groupDetails.modal.html'
            controller:  'LMNGroupDetailsController'
            size: 'lg'
            resolve:
               groupType: () -> groupType
               groupName: () -> groupName
        ).result.then (result)->
            if result.response is 'refresh'
                $scope.getGroups ($scope.identity.user)



    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
           return
        if $scope.identity.user is null
           return
        if $scope.identity.user is 'root'
           # $scope.identity.user = 'hulk'
           return
        $scope.getGroups($scope.identity.user)
        return
