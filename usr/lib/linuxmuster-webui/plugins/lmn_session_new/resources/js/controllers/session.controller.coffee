angular.module('lmn.session_new').controller 'LMNSessionController', ($scope, $http, $location, $route, $uibModal, $window, $q, $interval, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap, filesystem, validation, identity, $rootScope, wait, userPassword, lmnSession, smbclient) ->

    $scope.stateChanged = false
    $scope.sessionChanged = false
    $scope.addParticipant = ''
    $scope.addSchoolClass = ''
    $scope.examMode = false
    $scope.file_icon = {
        'powerpoint': "far fa-file-powerpoint",
        'text': "far fa-file-alt",
        'code': "far fa-file-code",
        'word': "far fa-file-word",
        'pdf': "far fa-file-pdf",
        'excel': "far fa-file-excel",
        'audio': "far fa-file-audio",
        'archive': "far fa-file-archive",
        'video': "far fa-file-video",
        'image': "far fa-file-image",
        'file': "far fa-file",
    }

    $scope.management = {
        'wifi': false,
        'internet': false,
        'printing': false,
    }

    $window.onbeforeunload = (event) ->
        if !$scope.sessionChanged
            return
        # Confirm before page reload
        return "Eventually not refreshing"

    $scope.$on("$destroy", () ->
        # Avoid confirmation on others controllers
        $scope.stopRefreshFiles()
        $scope.stopRefreshParticipants()
        $window.onbeforeunload = undefined
    )

    $scope.$on("$locationChangeStart", (event) ->
        # TODO : handle logout if session is changed
        if $scope.sessionChanged
            if !confirm(gettext('Do you really want to quit this session ? You can restart it later if you want.'))
                event.preventDefault()
                return
        $window.onbeforeunload = undefined
    )

    $scope.translation ={
        addStudent: gettext('Add Student')
        addClass: gettext('Add Class')
    }

    $scope.sorts = [
        {
            name: gettext('Lastname')
            fx: (x) -> x.sn + ' ' + x.givenName
        }
        {
            name: gettext('Login name')
            fx: (x) -> x.sAMAccountName
        }
        {
            name: gettext('Firstname')
            fx: (x) -> x.givenName
        }
        {
            name: gettext('Email')
            fx: (x) -> x.mail
        }
    ]

    $scope.sort = $scope.sorts[0]

    $scope.backToSessionList = () ->
        $location.path('/view/lmn/sessionsList')

    $scope.session = lmnSession.current
    $scope.extExamUsers = lmnSession.extExamUsers
    $scope.examUsers = lmnSession.examUsers
    $scope.examMode = lmnSession.examMode

    lmnSession.createWorkingDirectory($scope.session.members).then () ->
        $scope.missing_schoolclasses = lmnSession.user_missing_membership.map((user) -> user.sophomorixAdminClass)
        $scope.missing_schoolclasses = [... new Set($scope.missing_schoolclasses)].join(',')

    $scope.refreshUsers = () ->
       return lmnSession.refreshUsers().then () ->
            $scope.extExamUsers = lmnSession.extExamUsers
            $scope.examUsers = lmnSession.examUsers
            $scope.examMode = lmnSession.examMode

    if $scope.session.type == 'schoolclass'
        title = " > " + gettext("Schoolclass") + " #{$scope.session.name}"
    else if $scope.session.type == 'room'
        title = " > " + gettext("Room") + " #{$scope.session.name}"
    else
        title = " > " + gettext("Group") + " #{$scope.session.name}"

    pageTitle.set(gettext('Session') + title )

    # Nothing defined, going back to session list
    if $scope.session.sid == ''
        $scope.backToSessionList()

    $scope.isStudent = (user) ->
        return ['student', 'examuser'].indexOf(user.sophomorixRole) > -1

    # Fix missing membership for share

    $scope.fixMembership = (group) ->
        $http.post('/api/lmn/groupmembership/membership', {
            action: 'addadmins',
            entity: $scope.identity.user,
            groupname: $scope.missing_schoolclasses,
            type: 'class'
        }).then (resp) ->
            if resp['data'][0] == 'ERROR'
                notify.error (resp['data'][1])
            if resp['data'][0] == 'LOG'
                notify.success gettext(resp['data'][1])
                $rootScope.identity = identity
                $scope.refresh_krbcc()

    $scope.refresh_krbcc = () ->
        smbclient.refresh_krbcc().then () ->
            for user in lmnSession.user_missing_membership
                position = $scope.session.members.indexOf(user)
                $scope.session.members[position].files = []
                lmnSession.createWorkingDirectory([user])
            identity.init().then () ->
                console.log("Identity renewed !")
                $scope.missing_schoolclasses = []

    # Refresh room users

    $scope.updateParticipants = () ->
        $http.get('/api/lmn/session/userInRoom').then (resp) ->
            if resp.data.usersList.length != 0
                $http.post("/api/lmn/session/userinfo", {users:resp.data.usersList}).then (rp) ->
                    $scope.session.members = rp.data
                    for userDetails in $scope.session.members
                        user = userDetails.cn
                        userDetails.computer = resp.data.objects[user].COMPUTER 

    $scope.stopRefreshParticipants = () ->
        if $scope.refresh_participants != undefined
            $interval.cancel($scope.refresh_participants)
        $scope.autorefresh_participants = false

    $scope.startRefreshParticipants = () ->
        $scope.updateParticipants()
        $scope.refresh_participants = $interval($scope.updateParticipants, 5000, 0)
        $scope.autorefresh_participants = true

    if $scope.session.type == 'room'
        $scope.startRefreshParticipants()

    # List working directory files

    $scope.get_file_icon = (filetype) ->
        return $scope.file_icon[filetype]

    $scope.updateFileList = () ->
        participants = $scope.session.members.filter((user) => user.files != 'ERROR' && user.files != 'ERROR-teacher');
        $http.post('/api/lmn/smbclient/listCollectDir', {participants:participants}).then (resp) ->
            for participant,files of resp.data
                for user in $scope.session.members
                    if user.cn == participant
                        if (typeof files.items == 'undefined')
                            # Error from backend
                            notify.error(gettext("Can not list directory from ") + user.displayName + ": " + files)
                        else
                            user.files = files.items
                        break

    $scope.stopRefreshFiles = () ->
        if $scope.refresh_files != undefined
            $interval.cancel($scope.refresh_files)
        $scope.autorefresh_files = false

    $scope.startRefreshFiles = () ->
        $scope.updateFileList()
        $scope.refresh_files = $interval($scope.updateFileList, 5000, 0)
        $scope.autorefresh_files = true

    # Management groups

    $scope.setManagementGroup = (group, participant) ->
        $scope.stateChanged = true
        if participant[group] == true
            group = "no#{group}"
        user = [participant.sAMAccountName]
        $http.post('/api/lmn/managementgroup', {group:group, users:user}).then((resp) ->
            notify.success("Group #{group} changed for #{user[0]}")
            $scope.stateChanged = false
        ).catch((err) ->
            notify.error(err.data.message)
            $scope.stateChanged = false
        )

    $scope.setManagementGroupAll = (group) ->
        $scope.stateChanged = true
        usersList = []
        $scope.management[group] = !$scope.management[group]

        for participant in $scope.session.members
            # Only change management group for student, and not others teachers
            if participant.sophomorixRole == 'student' or participant.sophomorixRole == 'examuser'
                participant[group] = $scope.management[group]
                usersList.push(participant.sAMAccountName)

        if $scope.management[group] == false
            group = "no#{group}"

        $http.post('/api/lmn/managementgroup', {group:group, users:usersList}).then((resp) ->
            notify.success("Group #{group} changed for #{usersList.join()}")
            $scope.stateChanged = false
        ).catch((err) ->
            notify.error(err.data.message)
            $scope.stateChanged = false
        )

    # Manage session

    $scope.renameSession = () ->
        lmnSession.rename($scope.session.sid, $scope.session.name).then (resp) ->
            $scope.session.name = resp

    $scope.killSession = () ->
        lmnSession.kill($scope.session.sid, $scope.session.name).then () ->
            $scope.backToSessionList()

    $scope.cloneSession = () ->
        memberslist = $scope.session.members.map((user) => user.cn);
        lmnSession.new(memberslist).then () ->
            $scope.backToSessionList()

    $scope.saveAsSession = () ->
        lmnSession.new($scope.session.members).then () ->
            $scope.sessionChanged = false
            # TODO : would be better to get the session id and simply set the current session
            # instead of going back to the sessions list
            # But for this sophomorix needs to return the session id when creating a new one
            $scope.backToSessionList()

    $scope.findUsers = (q) ->
        return $http.get("/api/lmn/session/user-search/#{q}").then (resp) ->
            return resp.data

    $scope.findSchoolClasses = (q) ->
        return $http.get("/api/lmn/session/schoolClass-search/#{q}").then (resp) ->
            return resp.data

    $scope.$watch 'addParticipant', () ->
        if $scope.addParticipant
            $http.post('/api/lmn/session/userinfo', {'users':[$scope.addParticipant.sAMAccountName]}).then (resp) ->
                new_participant = resp.data[0]
                $scope.addParticipant = ''
                if !$scope.session.generated
                    # Real session: must be added in LDAP
                    $http.post('/api/lmn/session/participants', {'users':[new_participant.sAMAccountName], 'session': $scope.session.sid})
                else
                    $scope.sessionChanged = true
                $scope.session.members.push(new_participant)
                $scope.refreshUsers()

    $scope.$watch 'addSchoolClass', () ->
        if $scope.addSchoolClass
            members = $scope.addSchoolClass.sophomorixMembers
            $http.post('/api/lmn/session/userinfo', {'users':members}).then (resp) ->
                new_participants = resp.data
                $scope.addSchoolClass = ''
                if !$scope.session.generated
                    # Real session: must be added in LDAP
                    $http.post('/api/lmn/session/participants', {'users':members, 'session': $scope.session.sid})
                else
                    $scope.sessionChanged = true
                $scope.session.members = $scope.session.members.concat(new_participants)
                $scope.refreshUsers()

    $scope.removeParticipant = (participant) ->
        deleteIndex = $scope.session.members.indexOf(participant)
        if deleteIndex != -1
            if $scope.session.generated
                # Not a real session, just removing from participants list displayed
                $scope.session.members.splice(deleteIndex, 1)
                $scope.sessionChanged = true
            else
                $http.patch('/api/lmn/session/participants', {'users':[participant.sAMAccountName], 'session': $scope.session.sid}).then () ->
                    $scope.session.members.splice(deleteIndex, 1)

    # Exam mode

    $scope.startExam = () ->
        if $scope.examMode
            return

        # End exam for a whole group
        messagebox.show({
            text: gettext('Do you really want to start a new exam?'),
            positive: gettext('Start exam mode'),
            negative: gettext('Cancel')
        }).then () ->
            wait.modal(gettext("Starting exam mode ..."), "spinner")
            $scope.stateChanged = true
            $scope.examMode = true
            $http.patch("/api/lmn/session/exam/start", {session: $scope.session}).then (resp) ->
                $scope.stateChanged = false
                lmnSession.getExamUsers()
                $scope.stopRefreshFiles()
                $rootScope.$emit('updateWaiting', 'done')

    $scope.stopExam = () ->
        if !$scope.examMode
            return

        # End exam for a whole group
        messagebox.show({
            text: gettext('Do you really want to end the current exam?'),
            positive: gettext('End exam mode'),
            negative: gettext('Cancel')
        }).then () ->
            wait.modal(gettext("Stopping exam mode ..."), "spinner")
            $scope.stateChanged = true
            $scope.examMode = false
            $http.patch("/api/lmn/session/exam/stop", {session: $scope.session}).then (resp) ->
                $scope.refreshUsers()
                $scope.stateChanged = false
                $rootScope.$emit('updateWaiting', 'done')
            $scope.stopRefreshFiles()

    $scope._stopUserExam = (user) ->
        # End exam for a specific user: backend promise without messagebox
        uniqSession = {
            'members': [user],
            'name': "#{user.sophomorixAdminClass}_#{user.sAMAccountName}_ENDED_FROM_#{identity.user}",
            'type': '',
        }
        return $http.patch("/api/lmn/session/exam/stop", {session: uniqSession})

    $scope.stopUserExam = (user) ->
        # End exam for a specific user
        messagebox.show({
            text: gettext('Do you really want to remove ' + user.displayName + ' from the exam of ' + user.examTeacher + '?'),
            positive: gettext('End exam mode'),
            negative: gettext('Cancel')
        }).then () ->
            wait.modal(gettext("Stopping exam mode ..."), "spinner")
            $scope._stopUserExam(user).then () ->
                $scope.refreshUsers().then () ->
                    $rootScope.$emit('updateWaiting', 'done')
                    notify.success(gettext('Exam mode stopped for user ') + user.displayName)

    $scope.stopRunningExams = () ->
        # End all running extern exams (run by other teachers)
        messagebox.show({
            text: gettext('Do you really want to end all running exams?'),
            positive: gettext('End exam mode'),
            negative: gettext('Cancel')
        }).then () ->
            promises = []
            for user in $scope.extExamUsers
                promises.push($scope._stopUserExam(user))
            for user in $scope.examUsers
                promises.push($scope._stopUserExam(user))
            wait.modal(gettext("Stopping exam mode ..."), "spinner")
            $q.all(promises).then () ->
                $scope.refreshUsers()
                $rootScope.$emit('updateWaiting', 'done')
                notify.success(gettext('Exam mode stopped for all users.'))

    $scope._checkExamUser = (username) ->
        if username.endsWith('-exam')
            messagebox.show(title: gettext('User in exam'), text: gettext('This user seems to be in exam. End exam mode before changing password!'), positive: 'OK')
            return true
        return false

    # Passwords

    $scope.showFirstPassword = (username) ->
        $scope.blurred = true
        # if user is exam user show InitialPassword of real user
        userPassword.showFirstPassword(username).then((resp) ->
            $scope.blurred = false
        )

    $scope.resetFirstPassword = (user, exam=false) ->
        userPassword.resetFirstPassword(user.cn)
        if exam
            userPassword.resetFirstPassword(user.examBaseCn)

    $scope.setRandomFirstPassword = (username) ->
        if not $scope._checkExamUser(username)
            userPassword.setRandomFirstPassword(username)

    $scope.setCustomPassword = (user, pwtype, exam=false) ->
        userList = [user]
        if exam
            examUser = {
                'sophomorixAdminClass': user.sophomorixAdminClass.slice(0,-5),
                'sn': user.sn,
                'givenName': user.givenName,
                'sAMAccountName': user.sAMAccountName.slice(0,-5)
            }
            userList.push(examUser)
        userPassword.setCustomPassword(userList, pwtype, exam)

    # Share and collect

    $scope.choose_items = (path, print_path, command, user) ->
        return $uibModal.open(
           templateUrl: '/lmn_session_new:resources/partial/selectFile.modal.html'
           controller: 'LMNSessionFileSelectModalController'
           scope: $scope
           resolve:
              action: () -> command
              path: () -> path
              print_path: () -> print_path
              user: () -> user
        ).result

    $scope.smbcopy_notify = (src, dst, name, user) ->
       smbclient.copy(src, dst, notify_success=false).then () ->
            notify.success(gettext("File #{name} shared to #{user}!"))

    $scope._share = (participant, items) ->
        share_path = "#{participant.homeDirectory}\\transfer\\#{identity.profile.sAMAccountName}"
        for item in items
            $scope.smbcopy_notify(item.path, share_path + '/' + item.name, item.name, participant.sAMAccountName )

#        $q.all(promises).then () ->
#            notify.success(gettext("Files shared!"))

    $scope.shareUser = (participant) ->
        # participants is an array containing one or all participants
        choose_path = "#{identity.profile.homeDirectory}\\transfer"
        print_path = "transfer"
        $scope.choose_items(choose_path, print_path, 'share', participant.sAMAccountName).then (result) ->
            if result.response is 'accept'
                $scope._share(participant, result.items)

    $scope.shareAll = () ->
        choose_path = "#{identity.profile.homeDirectory}\\transfer"
        print_path = "transfer"
        $scope.choose_items(choose_path, print_path,'share', 'all').then (result) ->
            if result.response is 'accept'
                for participant in $scope.session.members
                    if $scope.isStudent(participant)
                        $scope._share(participant, result.items)

    $scope._leading_zero = (int) ->
        if "#{int}".length == 1
            return "0#{int}"
        return int

    $scope.now = () ->
        # Formating date for collect directory
        date = new Date()
        year = date.getFullYear()
        month = $scope._leading_zero(date.getMonth()+1)
        day = $scope._leading_zero(date.getDate())
        hours = $scope._leading_zero(date.getHours())
        minutes = $scope._leading_zero(date.getMinutes())
        seconds = $scope._leading_zero(date.getSeconds())
        return "#{year}#{month}#{day}-#{hours}#{minutes}#{seconds}"

    $scope._collect = (command, items, collect_path) ->
        promises = []
        if command is 'copy'
            for item in items
                promises.push(smbclient.copy(item.path, collect_path + '/' + item.name, notify_success=false))
        if command is 'move'
            for item in items
                promises.push(smbclient.move(item.path, collect_path + '/' + item.name, notify_success=false))
        return $q.all(promises)

    $scope.collectAll = (command) ->
        # command is copy or move

        promises = []
        now = $scope.now()
        transfer_directory = "#{$scope.session.type}_#{$scope.session.name}_#{now}"
        collect_path = "#{identity.profile.homeDirectory}\\transfer\\collected\\#{transfer_directory}"
        smbclient.createDirectory(collect_path)

        promises = []
        for participant in $scope.session.members
            if $scope.isStudent(participant)
                dst = "#{collect_path}\\#{participant.sAMAccountName}"
                items = [{
                    "path": "#{participant.homeDirectory}\\transfer\\#{$scope.identity.user}\\_collect",
                    "name": ""
                }]
                promises.push($scope._collect(command, items, dst))
        $q.all(promises).then () ->
            # _collect directory was moved, so recreating empty working diretories for all
            lmnSession.createWorkingDirectory($scope.session.members).then () ->
                $scope.missing_schoolclasses = lmnSession.user_missing_membership.map((user) -> user.sophomorixAdminClass).join(',')
            notify.success(gettext("Files collected!"))

    $scope.collectUser = (command, participant) ->
        # participant is only one user
        # command is copy or move

        now = $scope.now()
        transfer_directory = "#{$scope.session.type}_#{$scope.session.name}_#{now}"
        collect_path = "#{identity.profile.homeDirectory}\\transfer\\collected\\#{transfer_directory}\\#{participant.sAMAccountName}"
        smbclient.createDirectory(collect_path)

        choose_path = "#{participant.homeDirectory}\\transfer\\#{$scope.identity.user}\\_collect"
        print_path = "transfer/#{$scope.identity.user}/_collect"
        $scope.choose_items(choose_path, print_path, command, participant.sAMAccountName).then (result) ->
            if result.response is 'accept'
                $scope._collect(command, result.items, collect_path).then () ->
                    notify.success(gettext("Files collected!"))

    $scope.browseCollected = () ->
        collect_path = "#{identity.profile.homeDirectory}\\transfer\\collected"
        $uibModal.open(
           templateUrl: '/lmn_session_new:resources/partial/selectFile.modal.html'
           controller: 'LMNSessionFileSelectModalController'
           scope: $scope
           resolve:
              action: () -> ''
              path: () -> collect_path
              print_path: () -> collect_path
              user: () -> ''
        )

angular.module('lmn.session_new').controller 'LMNSessionFileSelectModalController', ($scope, $uibModalInstance, gettext, notify, $http, action, path, messagebox, smbclient, user, print_path) ->

    $scope.action = action # copy, move or share
    $scope.init_path = path
    $scope.current_path = path
    $scope.parent_path = []
    $scope.toggleAllStatus = false
    $scope.count_selected = 0
    $scope.uploadProgress = []
    $scope.user = user
    $scope.print_path = print_path

    $scope.load_path = (path) ->
        smbclient.list(path).then (data) ->
            $scope.items = data.items
            $scope.parent_path.push($scope.current_path)
            $scope.current_path = path

    $scope.toggleAll = () ->
        for item in $scope.items
            item.selected = !item.selected

    $scope.refreshSelected = () ->
        $scope.count_selected = $scope.items.filter((item) -> item.selected == true).length

    $scope.back = () ->
        path = $scope.parent_path.at(-1)
        smbclient.list(path).then (data) ->
            $scope.items = data.items
            $scope.current_path = path
            $scope.parent_path.pop()

    $scope.load_path($scope.init_path)

    $scope.save = () ->
        itemsToTrans =  []
        for item in $scope.items
            if item['selected']
                itemsToTrans.push(item)
        if itemsToTrans.length == 0
            notify.info(gettext('Please select at least one file!'))
            return
        $uibModalInstance.close(response: 'accept', items: itemsToTrans)

    $scope.close = () ->
        $uibModalInstance.dismiss()

    $scope.create_dir = (path) ->
        messagebox.prompt(gettext('Directory name :'), '').then (msg) ->
            new_path = $scope.current_path + '/' + msg.value
            smbclient.createDirectory(new_path).then (data) ->
                notify.success(new_path + gettext(' created '))
                $scope.load_path($scope.current_path)
            .catch (resp) ->
                notify.error(gettext('Error during creating: '), resp.data.message)

    $scope.delete_file = (path) ->
        messagebox.show({
            text: gettext('Are you sure you want to delete permanently the file ' + path + '?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then () ->
            smbclient.delete_file(path).then (data) ->
                notify.success(path + gettext(' deleted !'))
                $scope.load_path($scope.current_path)
            .catch (resp) ->
                notify.error(gettext('Error during deleting : '), resp.data.message)

    $scope.delete_dir = (path) ->
        messagebox.show({
            text: gettext('Are you sure you want to delete permanently the directory ' + path + '?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then () ->
            smbclient.delete_dir(path).then (data) ->
                notify.success(path + gettext(' deleted !'))
                $scope.load_path($scope.current_path)
            .catch (resp) ->
                notify.error(gettext('Error during deleting : '), resp.data.message)


    $scope.rename = (item) ->
        old_path = item.path
        messagebox.prompt(gettext('New name :'), item.name).then (msg) ->
            new_path = $scope.current_path + '/' + msg.value
            smbclient.move(old_path, new_path).then (data) ->
                notify.success(old_path + gettext(' renamed to ') + new_path)
                $scope.load_path($scope.current_path)
            .catch (resp) ->
                notify.error(gettext('Error during renaming: '), resp.data.message)

    $scope.areUploadsFinished = () ->
        numUploads = $scope.uploadProgress.length
        if numUploads == 0
            return true

        globalProgress = 0
        for p in $scope.uploadProgress
            globalProgress += p.progress

        return numUploads * 100 == globalProgress

    $scope.sambaSharesUploadBegin = ($flow) ->
        $scope.uploadProgress = []
        $scope.uploadFiles = []
        for file in $flow.files
            $scope.uploadFiles.push(file.name)

        $scope.files_list = $scope.uploadFiles.join(', ')
        smbclient.startFlowUpload($flow, $scope.current_path).then (resp) ->
            notify.success(gettext('Uploaded ') + $scope.files_list)
            $scope.load_path($scope.current_path)
        , null, (progress) ->
            $scope.uploadProgress = progress.sort((a, b) -> a.name > b.name)
