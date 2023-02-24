angular.module('lmn.session_new').controller 'LMNSessionController', ($scope, $http, $location, $route, $uibModal, $window, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap, filesystem, validation, $rootScope, wait, userPassword, lmnSession) ->
    pageTitle.set(gettext('Session'))

    $scope.changeState = false
    $scope.addParticipant = ''
    $scope.addSchoolClass = ''

    $window.onbeforeunload = (event) ->
        if $scope.session.ID == '' or $scope.session.participants.length == 0
            return
        # Confirm before page reload
        return "Eventually not refreshing"

    $scope.$on("$destroy", () ->
        # Avoid confirmation on others controllers
        $window.onbeforeunload = undefined
    )

    $scope.$on("$locationChangeStart", (event) ->
        if $scope.session.ID != '' and $scope.session.participants.length > 0
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

    $scope.fields = {
        sAMAccountName:
            visible: true
            name: gettext('Userdata')
        transfer:
            visible: true
            name: gettext('Transfer')
        examModeSupervisor:
            visible: true
            name: gettext('Exam-Supervisor')
        sophomorixRole:
            visible: false
            name: gettext('sophomorixRole')
        exammode:
            visible: true
            icon:"fa fa-graduation-cap"
            title: gettext('Exam-Mode')
            checkboxAll: false
            examBox: true
            checkboxStatus: false
        wifi:
            visible: true
            icon:"fa fa-wifi"
            title: gettext('Wifi-Access')
            checkboxAll: true
            checkboxStatus: false
        internet:
            visible: true
            icon:"fa fa-globe"
            title: gettext('Internet-Access')
            checkboxAll: true
            checkboxStatus: false
        intranet:
            visible: false
            icon:"fa fa-server"
            title: gettext('Intranet Access')
            checkboxAll: true
        webfilter:
            visible: false
            icon:"fa fa-filter"
            title: gettext('Webfilter')
            checkboxAll: true
            checkboxStatus: false
        printing:
            visible: true
            icon:"fa fa-print"
            title: gettext('Printing')
            checkboxAll: true
            checkboxStatus: false
    }

    $scope.backToSessionList = () ->
        $location.path('/view/lmn/sessionsList')

    $scope.session = lmnSession.current
    if $scope.session.ID == ''
        $scope.backToSessionList()

    $scope.setManagementGroup = (group, participant) ->
        $scope.changeState = true
        if participant[group] == true
            group = "no#{group}"
        user = [participant.sAMAccountName]
        $http.post('/api/lmn/managementgroup', {group:group, users:user}).then (resp) ->
            notify.success("Group #{group} changed for #{user[0]}")
            $scope.changeState = false

    $scope.selectAll = (id) ->
        console.log('later')
    #        if item is 'exammode'
    #            managementgroup = 'exammode_boolean'

    $scope.setManagementGroupAll = (group) ->
        $scope.changeState = true
        usersList = []
        new_value = !$scope.fields[group].checkboxStatus

        for participant in $scope.session.participants
            participant[group] = new_value
            usersList.push(participant.sAMAccountName)

        if new_value == false
            group = "no#{group}"

        $http.post('/api/lmn/managementgroup', {group:group, users:usersList}).then (resp) ->
            notify.success("Group #{group} changed for #{usersList.join()}")
            $scope.changeState = false

    $scope.renameSession = () ->
        lmnSession.rename($scope.session.ID, $scope.session.COMMENT).then (resp) ->
            $scope.session.COMMENT = resp

    $scope.killSession = () ->
        lmnSession.kill($scope.session.ID, $scope.session.COMMENT).then () ->
            $scope.backToSessionList()

    $scope.saveAsSession = () ->
        lmnSession.new($scope.session.participants).then () ->
            # TODO : would be better to get the session id and simply set the current session
            # instead of going back to the sessions list
            # But for this sophomorix needs to return the session id when creating a new one
            $scope.backToSessionList()

    $scope.showGroupDetails = (index, groupType, groupName) ->
       $uibModal.open(
          templateUrl: '/lmn_groupmembership:resources/partial/groupDetails.modal.html'
          controller:  'LMNGroupDetailsController'
          size: 'lg'
          resolve:
            groupType: () -> groupType
            groupName: () -> groupName
       )

    $scope.showRoomDetails = () ->
        $http.get('/api/lmn/session/userInRoom').then (resp) ->
            if resp.data == 0
                messagebox.show(title: gettext('Info'), text: gettext('Currenty its not possible to determine your room, try to login into your computer again.'), positive: 'OK')
            else
                usersInRoom=resp.data
                $uibModal.open(
                   templateUrl: '/lmn_session_new:resources/partial/roomDetails.modal.html'
                   controller:  'LMNRoomDetailsController'
                   size: 'lg'
                   resolve:
                     usersInRoom: () -> usersInRoom
                )

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
                    $http.post('/api/lmn/session/participants', {'users':[new_participant.sAMAccountName], 'session': $scope.session.ID})
                $scope.session.participants.push(new_participant)

    $scope.$watch 'addSchoolClass', () ->
        if $scope.addSchoolClass
            members = Object.keys($scope.addSchoolClass.members)
            $http.post('/api/lmn/session/userinfo', {'users':members}).then (resp) ->
                new_participants = resp.data
                $scope.addSchoolClass = ''
                if !$scope.session.generated
                    # Real session: must be added in LDAP
                    $http.post('/api/lmn/session/participants', {'users':members, 'session': $scope.session.ID})
                $scope.session.participants = $scope.session.participants.concat(new_participants)

    $scope.removeParticipant = (participant) ->
        deleteIndex = $scope.session.participants.indexOf(participant)
        if deleteIndex != -1
            if $scope.session.generated
                # Not a real session, just removing from participants list displayed
                $scope.session.participants.splice(deleteIndex, 1)
            else
                $http.patch('/api/lmn/session/participants', {'users':[participant.sAMAccountName], 'session': $scope.session.ID}).then () ->
                    $scope.session.participants.splice(deleteIndex, 1)

    $scope.changeExamSupervisor = (participant, supervisor) ->
        $http.post('/api/lmn/session/sessions', {action: 'change-exam-supervisor', supervisor: supervisor, participant: participant}).then (resp) ->

    $scope.endExam = (participant, supervisor,session, sessionName) ->
        $http.patch("/api/lmn/session/exam/#{sessionName}", {supervisor: supervisor, participant: participant}).then (resp) ->
            $scope.getParticipants(session)

    $scope._checkExamUser = (username) ->
        if username.endsWith('-exam')
            messagebox.show(title: gettext('User in exam'), text: gettext('This user seems to be in exam. End exam mode before changing password!'), positive: 'OK')
            return true
        return false

    $scope.showFirstPassword = (username) ->
        $scope.blurred = true
        # if user is exam user show InitialPassword of real user
        username = username.replace('-exam', '')
        userPassword.showFirstPassword(username).then((resp) ->
            $scope.blurred = false
        )
    $scope.resetFirstPassword = (username) ->
        if not $scope._checkExamUser(username)
            userPassword.resetFirstPassword(username)

    $scope.setRandomFirstPassword = (username) ->
        if not $scope._checkExamUser(username)
            userPassword.setRandomFirstPassword(username)

    $scope.setCustomPassword = (user, pwtype) ->
        if not $scope._checkExamUser(user.sAMAccountName)
            userPassword.setCustomPassword(user, pwtype)

    $scope.userInfo = (user) ->
        $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/userDetails.modal.html'
            controller: 'LMNUserDetailsController'
            size: 'lg'
            resolve:
                id: () -> user
                role: () -> 'students'
        )


    typeIsArray = Array.isArray || ( value ) -> return {}.toString.call( value ) is '[object Array]'

    validateResult = (resp) ->
        if resp['data'][0] == 'ERROR'
            notify.error (resp['data'][1])
        if resp['data'][0] == 'LOG'
            notify.success gettext(resp['data'][1])



    $scope.shareTrans = (command, senders, receivers, sessioncomment) ->
        # When share with session we get the whole session as an array.
        # The function on the other hand waits for an array containing just the  usernames so we extract
        # these into an array
        # If share option is triggered with just one user we get this user  as a string. If so we also have
        # to put it in an array
        bulkMode = 'false'
        participantsArray = []
        if typeIsArray receivers
            bulkMode = 'true'
            for receiver in receivers
                participantsArray.push receiver['sAMAccountName']
        else
            participantsArray.push receivers
        receivers = participantsArray

        $uibModal.open(
           templateUrl: '/lmn_session_new:resources/partial/selectFile.modal.html'
           controller: 'LMNSessionFileSelectModalController'
           resolve:
              action: () -> 'share'
              bulkMode: () -> bulkMode
              senders: () -> senders
              receivers: () -> receivers
              command: () -> command
              sessionComment: () -> sessioncomment
        ).result.then (result) ->
           if result.response is 'accept'
               wait.modal(gettext('Sharing files...'), 'progressbar')
               $http.post('/api/lmn/session/trans', {command: command, senders: senders, receivers: receivers, files: result.files, session: sessioncomment}).then (resp) ->
                   $rootScope.$emit('updateWaiting', 'done')
                   validateResult(resp)


    $scope.collectTrans = (command, senders, receivers, sessioncomment) ->
        # When collect from session we already get the users in an array containing the user objects.
        # If collect option is triggered with just on use we get this user as an object. If so we also
        # have to put it in an array.
        #console.log (command)
        #console.log (senders)
        bulkMode = 'false'
        participantsArray = []
        if typeIsArray senders
            bulkMode = 'true'
        else
            participantsArray.push senders
            senders = participantsArray
        transTitle = 'transfer'
        #console.log (bulkMode)
        $uibModal.open(
           templateUrl: '/lmn_session_new:resources/partial/selectFile.modal.html'
           controller: 'LMNSessionFileSelectModalController'
           resolve:
              action: () -> 'collect'
              bulkMode: () -> bulkMode
              senders: () -> senders
              receivers: () -> receivers
              command: () -> command
              sessionComment: () -> sessioncomment
        ).result.then (result) ->
            if result.response is 'accept'
                #return
                wait.modal(gettext('Collecting files...'), 'progressbar')
                if command is 'copy'
                    $http.post('/api/lmn/session/trans', {command: command, senders: senders, receivers: receivers, files: result.files, session: sessioncomment}).then (resp) ->
                        $rootScope.$emit('updateWaiting', 'done')
                        validateResult(resp)
                if command is 'move'
                    $http.post('/api/lmn/session/trans', {command: command, senders: senders, receivers: receivers, files: result.files, session: sessioncomment}).then (resp) ->
                        $rootScope.$emit('updateWaiting', 'done')
                        validateResult(resp)


    $scope.notImplemented = (user) ->
                messagebox.show(title: gettext('Not implemented'), positive: 'OK')

    # Websession part

    $scope.getWebConferenceEnabled = () ->
        $http.get('/api/lmn/websession/webConferenceEnabled').then (resp) ->
            if resp.data == true
                $scope.websessionEnabled = true
                $scope.websessionGetStatus()
            else
                $scope.websessionEnabled = false;

    $scope.websessionIsRunning = false

    $scope.websessionGetStatus = () ->
        sessionname = $scope.session.COMMENT + "-" + $scope.session.ID
        $http.get("/api/lmn/websession/webConference/#{sessionname}").then (resp) ->
            if resp.data["status"] is "SUCCESS"
                if resp.data["data"]["status"] == "started"
                    $scope.websessionIsRunning = true
                else
                    $scope.websessionIsRunning = false
                $scope.websessionID = resp.data["data"]["id"]
                $scope.websessionAttendeePW = resp.data["data"]["attendeepw"]
                $scope.websessionModeratorPW = resp.data["data"]["moderatorpw"]
            else
                $scope.websessionIsRunning = false

    $scope.websessionToggle = () ->
        if $scope.websessionIsRunning == false
            $scope.websessionStart()
        else
            $scope.websessionStop()

    $scope.websessionStop = () ->
        $http.post('/api/lmn/websession/endWebConference', {id: $scope.websessionID, moderatorpw: $scope.websessionModeratorPW}).then (resp) ->
            $http.delete("/api/lmn/websession/webConference/#{$scope.websessionID}").then (resp) ->
                if resp.data["status"] == "SUCCESS"
                    notify.success gettext("Successfully stopped!")
                    $scope.websessionIsRunning = false
                else
                    notify.error gettext('Cannot stop entry!')

    $scope.websessionStart = () ->
        tempparticipants = []
        for participant in $scope.session.participants
            tempparticipants.push(participant.sAMAccountName)

        $http.post('/api/lmn/websession/webConferences', {sessionname: $scope.session.COMMENT + "-" + $scope.session.ID, sessiontype: "private", sessionpassword: "", participants: tempparticipants}).then (resp) ->
            if resp.data["status"] is "SUCCESS"
                $scope.websessionID = resp.data["id"]
                $scope.websessionAttendeePW = resp.data["attendeepw"]
                $scope.websessionModeratorPW = resp.data["moderatorpw"]
                $http.post('/api/lmn/websession/startWebConference', {sessionname: $scope.session.COMMENT + "-" + $scope.session.ID, id: $scope.websessionID, attendeepw: $scope.websessionAttendeePW, moderatorpw: $scope.websessionModeratorPW}).then (resp) ->
                    if resp.data["returncode"] is "SUCCESS"
                        $http.post('/api/lmn/websession/joinWebConference', {id: $scope.websessionID, password: $scope.websessionModeratorPW, name: $scope.identity.profile.sn + ", " + $scope.identity.profile.givenName}).then (resp) ->
                            $scope.websessionIsRunning = true
                            window.open(resp.data, '_blank')
                    else
                        notify.error gettext('Cannot start websession! Try to reload page!')
            else
                notify.error gettext("Create session failed! Try again later!")

# Websession part

angular.module('lmn.session_new').controller 'LMNRoomDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, usersInRoom) ->
        $scope.usersInRoom = usersInRoom

        $scope.close = () ->
            $uibModalInstance.dismiss()

angular.module('lmn.session_new').controller 'LMNSessionFileSelectModalController', ($scope, $uibModalInstance, gettext, notify, $http, bulkMode, senders, receivers, action, command, sessionComment, messagebox) ->
    $scope.bulkMode = bulkMode
    $scope.senders = senders
    $scope.receivers = receivers
    $scope.action = action
    $scope.command = command

    $scope.setTransferPath = (username) ->
        role = $scope.identity.profile.sophomorixRole
        school = $scope.identity.profile.activeSchool
        $scope.transferPath = '/srv/webuiUpload/'+school+'/'+role+'/'+username+'/'
        # create tmp dir for upload
        $scope.createDir($scope.transferPath)
        $scope.owner = username


    $scope.save = () ->
        filesToTrans =  []
        angular.forEach $scope.files['TREE'], (file, id) ->
            if file['checked'] is true
                filesToTrans.push(id)
        if filesToTrans.length == 0
            notify.info(gettext('Please select at least one file!'))
            return
        $uibModalInstance.close(response: 'accept', files: filesToTrans, bulkMode: bulkMode)

    $scope.saveBulk = () ->
        $uibModalInstance.close(response: 'accept', files: 'All', bulkMode: bulkMode)

    $scope.close = () ->
        $uibModalInstance.dismiss()

    $scope.share = () ->
        $http.post('/api/lmn/session/trans-list-files', {user: senders[0]}).then (resp) ->
            $scope.files = resp['data'][0]
            $scope.filesList = resp['data'][1]

    $scope.collect = () ->
        if bulkMode is 'false'
            $http.post('/api/lmn/session/trans-list-files', {user: senders, subfolderPath: receivers[0]+'_'+sessionComment}).then (resp) ->
                $scope.files = resp['data'][0]
                $scope.filesList = resp['data'][1]

    $scope.createDir = (path) ->
        $http.post('/api/lmn/create-dir', {filepath: path})

    $scope.removeFile = (file) ->
        role = $scope.identity.profile.sophomorixRole
        school = $scope.identity.profile.activeSchool
        path = $scope.identity.profile.homeDirectory+'\\transfer\\'+file
        messagebox.show({
            text: gettext('Are you sure you want to delete permanently the file ' + file + '?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then () ->
            $http.post('/api/lmn/smbclient/unlink', {path: path}).then (resp) ->
                notify.success(gettext("File " + file + " removed"))
                delete $scope.files['TREE'][file]
                $scope.files['COUNT']['files'] = $scope.files['COUNT']['files'] - 1
                pos = $scope.filesList.indexOf(file)
                $scope.filesList.splice(pos, 1)

    $scope.removeDir = (file) ->
        role = $scope.identity.profile.sophomorixRole
        school = $scope.identity.profile.activeSchool
        path = '/srv/samba/schools/'+school+'/'+role+'/'+$scope.identity.user+'/transfer/'+file
        messagebox.show({
            text: gettext('Are you sure you want to delete permanently this directory and its content: ' + file + '?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then () ->
            $http.post('/api/lmn/remove-dir', {filepath: path}).then (resp) ->
                notify.success(gettext("Directory " + file + " removed"))
                delete $scope.files['TREE'][file]
                $scope.files['COUNT']['files'] = $scope.files['COUNT']['files'] - 1
                pos = $scope.filesList.indexOf(file)
                $scope.filesList.splice(pos, 1)

    $scope.setTransferPath($scope.identity.user)
    if action is 'share'
        $scope.share()
    else
        $scope.collect()
