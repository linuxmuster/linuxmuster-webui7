angular.module('lmn.groupmembership').config ($routeProvider) ->
  $routeProvider.when '/view/lmn/groupmembership',
    controller: 'LMNGroupMembershipController'
    templateUrl: '/lmn_groupmembership:resources/partial/index.html'

angular.module('lmn.groupmembership').controller 'LMNGroupMembershipController', ($rootScope, $scope, $http, $window, identity, $uibModal, gettext, notify, pageTitle, messagebox, validation, smbclient) ->

  $scope.need_krbcc_refresh = false

  pageTitle.set(gettext('Enrolle'))
  $scope.show_schoolclasses = true
  $scope.show_projects = true
  $scope.show_printers = true
  $scope.loading_schoolclasses = true
  $scope.loading_projects = true
  $scope.loading_printers = true

  $scope.$on("$destroy", () ->
    warning = "These changes can only take effect if the session is renewed, otherwise it will be active after the next
        logout/login. It could be useful for the session plugin to do it now."
    if $scope.need_krbcc_refresh
      messagebox.show(text: warning, positive: 'Do it now', negative: 'Later').then () ->
        $scope.refresh_krbcc()
  )

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

  $scope.checkInverse = (sort ,currentSort) ->
    if sort == currentSort
      $scope.sortReverse = !$scope.sortReverse
    else
      $scope.sortReverse = false

  $scope.changeState = false

  $scope.setMembership = (group) ->
    $scope.changeState = true
    sophomorix_type_map = {'printer': 'group', 'adminclass': 'class', 'project': 'project'}
    if group.sophomorixType == 'printer'
        action = if group.membership then 'removemembers' else 'addmembers'
    else
        # TODO: seems to be wrong for projects
        action = if group.membership then 'removeadmins' else 'addadmins'

    $http.post('/api/lmn/groupmembership/membership', {
        action: action,
        entity: $scope.identity.user,
        groupname: group.groupname,
        type: sophomorix_type_map[group.sophomorixType]
    }).then (resp) ->
        if resp['data'][0] == 'ERROR'
            notify.error (resp['data'][1])
        if resp['data'][0] == 'LOG'
            notify.success gettext(resp['data'][1])
            group.membership = !group.membership
            $scope.changeState = false
            $rootScope.identity = identity
            $scope.need_krbcc_refresh = true
            identity.init().then () ->
                console.log("Identity renewed !")

  $scope.refresh_krbcc = () ->
    smbclient.refresh_krbcc().then(() -> $scope.need_krbcc_refresh = false)

  $scope.filterGroupType = (val) ->
    return (dict) ->
      dict['type'] == val

  $scope.getGroups = (username) ->
    $http.get('/api/lmn/groupmembership/projects').then (resp) ->
      $scope.projects = resp.data
      $scope.loading_projects = false
    $http.get('/api/lmn/groupmembership/printers').then (resp) ->
      $scope.printers = resp.data
      $scope.loading_printers = false
    $http.get('/api/lmn/groupmembership/schoolclasses').then (resp) ->
      $scope.classes = resp.data
      $scope.loading_schoolclasses = false

  $scope.createProject = () ->
    messagebox.prompt(gettext('Project Name'), '').then (msg) ->
      if not msg.value
        return
      test = validation.isValidProjectName(msg.value)
      if test != true
        notify.error gettext(test)
        return
      $http.post('/api/lmn/groupmembership/projects/' + msg.value).then (resp) ->
        if resp.data[0] is 'ERROR'
            notify.error gettext(resp.data[1])
        else
            if resp.data[0] is 'LOG' 
                notify.success gettext('Project Created')
                identity.init().then () ->
                        console.log("Identity renewed !")
                        $scope.getGroups ($scope.identity.user)
            else
                notify.info gettext('Something unusual happened')
        

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

  $scope.projectIsJoinable = (project) ->
    return project['sophomorixJoinable'] or project.admin or identity.profile.isAdmin or $scope.identity.profile.projects.indexOf(project['cn']) > -1

  $scope.resetAll = (type) ->
      warning = gettext('Are you sure to reset all admin memberships for this? This is actually only necessary to start a new empty school year. This cannot be undone!')
      messagebox.show(text: warning, positive: 'Delete', negative: 'Cancel').then () ->
          msg = messagebox.show(progress: true)
          all_groups = ''
          if type == 'class'
              for _class in $scope.classes
                  all_groups += _class.groupname + ','

          if type == 'project'
              for project in $scope.projects
                  all_groups += project.groupname + ','

          $http.post('/api/lmn/groupmembership/resetadmins', {type: type, all_groups: all_groups}).then (resp) ->
              notify.success gettext('Admin membership reset')
          .finally () ->
              msg.close()

  $scope.$watch 'identity.user', ->
    if $scope.identity.user is undefined
      return
    if $scope.identity.user is null
      return
    if $scope.identity.user is 'root'
      return
    $scope.getGroups($scope.identity.user)
    return

angular.module('lmn.groupmembership').controller 'LMNGroupDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, groupType, groupName) ->

        $scope.showAdminDetails = true
        $scope.showMemberDetails = true
        $scope.changeState = false
        $scope.editGroup = false

        $scope.hidetext = gettext("Hide")
        $scope.showtext = gettext("Show")

        $scope.changeMaillist = () ->
            $scope.changeState = true
            option = if $scope.maillist then '--maillist' else '--nomaillist'
            $http.post('/api/lmn/groupmembership/groupoptions/' + $scope.groupName, {option: option, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                $scope.changeState = false

        $scope.changeJoin = () ->
            $scope.changeState = true
            option = if $scope.joinable then '--join' else '--nojoin'
            $http.post('/api/lmn/groupmembership/groupoptions/' + $scope.groupName, {option: option, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                $scope.changeState = false

        $scope.changeHide = () ->
            $scope.changeState = true
            option = if $scope.hidden then '--hide' else '--nohide'
            $http.post('/api/lmn/groupmembership/groupoptions/' + $scope.groupName, {option: option, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                $scope.changeState = false

        $scope.killProject = (project) ->
             messagebox.show(text: "Do you really want to delete '#{project}'? This can't be undone!", positive: 'Delete', negative: 'Cancel').then () ->
                msg = messagebox.show(progress: true)
                $http.delete('/api/lmn/groupmembership/projects/' + project).then (resp) ->
                    if resp['data'][0] == 'ERROR'
                        notify.error (resp['data'][1])
                    if resp['data'][0] == 'LOG'
                        notify.success gettext(resp['data'][1])
                        $uibModalInstance.close(response: 'refresh')
                .finally () ->
                    msg.close()

        $scope.text = {
                'addAsAdmin' : gettext('Move to admin group'),
                'removeFromAdmin' : gettext('Remove from admin group'),
                'remove' : gettext('Remove')
        }

        $scope.killSchoolclass = (schoolclass) ->
             messagebox.show(text: "Do you really want to delete '#{schoolclass}'? This can't be undone!", positive: 'Delete', negative: 'Cancel').then () ->
                msg = messagebox.show(progress: true)
                $http.delete('/api/lmn/groupmembership/schoolclass/' + schoolclass).then (resp) ->
                    if resp['data'][0] == 'ERROR'
                        notify.error (resp['data'][1])
                    if resp['data'][0] == 'LOG'
                        notify.success gettext(resp['data'][1])
                        $uibModalInstance.close(response: 'refresh')
                .finally () ->
                    msg.close()

        $scope.formatDate = (date) ->
            if (date == "19700101000000.0Z")
                return $scope.nevertext
            else if (date == undefined)
                return "undefined"
            else
                # Sophomorix date format is yyyyMMddhhmmss.0Z
                year  = date.slice(0,4)
                month = +date.slice(4,6) - 1 # Month start at 0
                day   = date.slice(6,8)
                hour  = date.slice(8,10)
                min   = date.slice(10,12)
                sec   = date.slice(12,14)
                return new Date(year, month, day, hour, min, sec)

        $scope.getGroupDetails = (group) ->
            groupType = group[0]
            groupName = group[1]
            $http.get('/api/lmn/groupmembership/groups/' + groupName).then (resp) ->
                $scope.groupName    = groupName

                if !resp.data.hasOwnProperty('GROUP')
                    notify.error(gettext("Can not read properties of this project."))
                    $scope.close()
                    return

                $scope.groupDetails = resp.data['GROUP'][groupName]
                $scope.adminList = resp.data['GROUP'][groupName]['sophomorixAdmins']
                if groupType == 'printergroup'
                    $scope.groupmemberlist = []
                else
                    $scope.groupmemberlist = resp.data['GROUP'][groupName]['sophomorixMemberGroups']
                $scope.groupadminlist = resp.data['GROUP'][groupName]['sophomorixAdminGroups']

                $scope.typeMap = {
                    'adminclass': 'class',
                    'project': 'project',
                    'printer': 'group',
                }
                $scope.type = $scope.typeMap[$scope.groupDetails['sophomorixType']]
                
                $scope.members = []
                for name,member of resp.data['MEMBERS'][groupName]
                    if member.sn != "null" # group member
                        $scope.members.push({
                            'sn':member.sn,
                            'givenName':member.givenName,
                            'login': member.sAMAccountName,
                            'sophomorixAdminClass':member.sophomorixAdminClass,
                            'sophomorixRole':member.sophomorixRole
                        })
                    else if groupType == 'printergroup'
                        $scope.groupmemberlist.push(member.sAMAccountName)

                $scope.admins = []
                for admin in $scope.adminList
                    member = resp.data['MEMBERS'][groupName][admin]
                    $scope.admins.push({
                        'sn':member.sn,
                        'givenName':member.givenName,
                        'sophomorixAdminClass':member.sophomorixAdminClass,
                        'sophomorixRole':member.sophomorixRole,
                        'login': member.sAMAccountName
                    })

                $scope.joinable = resp.data['GROUP'][groupName]['sophomorixJoinable'] == 'TRUE'
                $scope.hidden = resp.data['GROUP'][groupName]['sophomorixHidden'] == 'TRUE'
                $scope.maillist = resp.data['GROUP'][groupName]['sophomorixMailList'] == 'TRUE'

                # Admin or admin of the project can edit members of a project
                # Only admins can change hide and join option for a class
                if identity.profile.isAdmin
                    $scope.editGroup = true
                else if (groupType == 'project') and ($scope.adminList.indexOf($scope.identity.user) >= 0)
                    $scope.editGroup = true
                else if (groupType == 'project') and ($scope.groupadminlist.indexOf($scope.identity.profile.sophomorixAdminClass) >= 0)
                    $scope.editGroup = true
                # List will not be updated later, avoir using it
                $scope.adminList = []

        $scope.filterLogin = (membersArray, login) ->
            return membersArray.filter((u) -> u.login == login).length == 0

        $scope.removeTeacherClass = (user) ->
            # Temporary wrapper to remove a teacher as member and admin from a class, to avoid conflicts
            $scope.removeMember(user)
            $scope.removeAdmin(user)

        $scope.addMember = (user) ->
            entity = ''
            if Array.isArray(user)
                for u in user
                    if $scope.filterLogin($scope.members, user.login)
                        entity += u.login + ","
            else
                if $scope.filterLogin($scope.members, user.login)
                    entity = user.login
            if not entity
                return
            $scope.changeState = true
            $http.post('/api/lmn/groupmembership/membership', {action: 'addmembers', entity: entity, groupname: groupName, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                    if Array.isArray(user)
                        $scope.members = $scope.members.concat(user.filter((u) -> $scope.members.indexOf(u) < 0))
                    else
                        $scope.members.push(user)
                $scope.changeState = false

        $scope.removeMember = (user) ->
            $scope.changeState = true
            $http.post('/api/lmn/groupmembership/membership', {action: 'removemembers', entity: user.login, groupname: groupName, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                    position = $scope.members.indexOf(user)
                    $scope.members.splice(position, 1)
                $scope.changeState = false

        $scope.addAdmin = (user) ->
            entity = ''
            if Array.isArray(user)
                for u in user
                    if $scope.filterLogin($scope.admins, user.login)
                        entity += u.login + ","
            else
                if $scope.filterLogin($scope.admins, user.login)
                    entity = user.login
            if not entity
                return
            $scope.changeState = true
            $http.post('/api/lmn/groupmembership/membership', {action: 'addadmins', entity: entity, groupname: groupName, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                    if Array.isArray(user)
                        $scope.admins = $scope.admins.concat(user.filter((u) -> $scope.admins.indexOf(u) < 0))
                        if $scope.type == 'class'
                            # Teachers are shown as members ...
                            $scope.members = $scope.members.concat(user.filter((u) -> $scope.members.indexOf(u) < 0))
                    else
                        $scope.admins.push(user)
                        if $scope.type == 'class'
                            # Teachers are shown as members ...
                            $scope.members.push(user)
                $scope.changeState = false

        $scope.removeAdmin = (user) ->
            $scope.changeState = true
            $http.post('/api/lmn/groupmembership/membership', {action: 'removeadmins', entity: user.login, groupname: groupName, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                    position = $scope.admins.indexOf(user)
                    $scope.admins.splice(position, 1)
                $scope.changeState = false

        $scope.addMemberGroup = (group) ->
            entity = ''
            if Array.isArray(group)
                for g in group
                    if $scope.groupmemberlist.indexOf(g) < 0
                        entity += g + ","
            else
                if $scope.groupmemberlist.indexOf(group) < 0
                    entity = group
            if not entity
                return
            $scope.changeState = true
            $http.post('/api/lmn/groupmembership/membership', {action: 'addmembergroups', entity: entity, groupname: groupName, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                    if Array.isArray(group)
                        $scope.groupmemberlist = $scope.groupmemberlist.concat(group.filter((g) -> $scope.groupmemberlist.indexOf(g) < 0))
                    else
                        $scope.groupmemberlist.push(group)
                $scope.changeState = false

        $scope.removeMemberGroup = (group) ->
            $scope.changeState = true
            $http.post('/api/lmn/groupmembership/membership', {action: 'removemembergroups', entity: group, groupname: groupName, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                    position = $scope.groupmemberlist.indexOf(group)
                    $scope.groupmemberlist.splice(position, 1)
                $scope.changeState = false

        $scope.addAdminGroup = (group) ->
            entity = ''
            if Array.isArray(group)
                for g in group
                    if $scope.groupadminlist.indexOf(g) < 0
                        entity += g + ","
            else
                if $scope.groupadminlist.indexOf(group) < 0
                    entity = group
            if not entity
                return
            $scope.changeState = true
            $http.post('/api/lmn/groupmembership/membership', {action: 'addadmingroups', entity: entity, groupname: groupName, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                    if Array.isArray(group)
                        $scope.groupadminlist = $scope.groupadminlist.concat(group.filter((g) -> $scope.groupadminlist.indexOf(g) < 0))
                    else
                        $scope.groupadminlist.push(group)
                $scope.changeState = false

        $scope.removeAdminGroup = (group) ->
            $scope.changeState = true
            $http.post('/api/lmn/groupmembership/membership', {action: 'removeadmingroups', entity: group, groupname: groupName, type: $scope.type}).then (resp) ->
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                    position = $scope.groupadminlist.indexOf(group)
                    $scope.groupadminlist.splice(position, 1)
                $scope.changeState = false

        $scope.demoteGroup = (group) ->
            $scope.removeAdminGroup(group)
            $scope.addMemberGroup(group)
            if (group == $scope.identity.profile.sophomorixAdminClass) and ($scope.filterLogin($scope.admins, $scope.identity.user))
                $scope.editGroup = false

        $scope.demoteMember = (user) ->
            $scope.removeAdmin(user)
            $scope.addMember(user)
            if (user.login == $scope.identity.user) and ($scope.groupadminlist.indexOf($scope.identity.profile.sophomorixAdminClass) < 0)
                $scope.editGroup = false

        $scope.elevateGroup = (group) ->
            $scope.removeMemberGroup(group)
            $scope.addAdminGroup(group)

        $scope.elevateMember = (user) ->
            $scope.removeMember(user)
            $scope.addAdmin(user)

        $scope._ =
            addMember: null
            addGroup: null
            addasadmin: false
            newGroup: []
            newUser: []
            noResults : false

        $scope.$watch '_.addMember', () ->
            if $scope._.addMember
                $scope._.newUser.push($scope._.addMember)
                $scope._.addMember = null

        $scope.$watch '_.addGroup', () ->
            if $scope._.addGroup
                $scope._.newGroup.push($scope._.addGroup)
                $scope._.addGroup = null

        $scope.addEntities = () ->
            $scope.UserSearchVisible = false
            if $scope.type == 'class'
                # Only teachers which are always admins in classes
                $scope._.addasadmin = true
            if $scope._.addasadmin
                $scope.addAdmin($scope._.newUser)
                $scope.addAdminGroup($scope._.newGroup)
            else
                $scope.addMember($scope._.newUser)
                $scope.addMemberGroup($scope._.newGroup)
            $scope._.newUser = []
            $scope._.newGroup = []
            $scope._.addasadmin = false


        $scope.placeholder_translate = {
            "login" : gettext("Type a name or login"),
            "class" : gettext("Type the class, e.g. 10a"),
            "group" : gettext("Type the group name, e.g. p_wifi"),
        }

        $scope.findUsers = (q) ->
            return $http.post("/api/lmn/find/user", {name:q}).then (resp) ->
                return resp.data
        $scope.findTeachers = (q) ->
            return $http.get("/api/lmn/find/teacher/" + q).then (resp) ->
                return resp.data
        $scope.findGroups = (q) ->
            return $http.get("/api/lmn/find/group/" + q).then (resp) ->
                groups = resp.data
                position = groups.indexOf($scope.groupName)
                console.log($scope.groupName, position)
                if position >= 0
                  groups.splice(position, 1)
                return groups
        $scope.findUsersGroup = (q) ->
            return $http.get("/api/lmn/find/usergroup/" + q).then (resp) ->
                return resp.data

        $scope.groupType = groupType
        $scope.getGroupDetails ([groupType, groupName])
        $scope.close = () ->
            $uibModalInstance.dismiss()



