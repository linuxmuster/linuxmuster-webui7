angular.module('lmn.session').controller 'LMNOldSessionFileSelectModalController', ($scope, $uibModalInstance, gettext, notify, $http, bulkMode, senders, receivers, action, command, sessionComment, messagebox) ->
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
        $http.post('/api/lmn/oldsession/trans-list-files', {user: senders[0]}).then (resp) ->
            $scope.files = resp['data'][0]
            $scope.filesList = resp['data'][1]

    $scope.collect = () ->
        if bulkMode is 'false'
            console.log (receivers[0])
            console.log (sessionComment)
            $http.post('/api/lmn/oldsession/trans-list-files', {user: senders, subfolderPath: receivers[0]+'_'+sessionComment}).then (resp) ->
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
        #$scope.setTransferPath($scope.identity.user)
        #$http.post('/api/lmn/oldsession/trans-list-files', {user: senders[0]}).then (resp) ->
        #    $scope.files = resp['data'][0]
        #    $scope.filesList = resp['data'][1]
    else
        $scope.collect()
        #if bulkMode is 'false'
        #    $http.post('/api/lmn/oldsession/trans-list-files', {user: senders}).then (resp) ->
        #        $scope.files = resp['data'][0]
        #        $scope.filesList = resp['data'][1]



angular.module('lmn.session').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/oldsession',
        controller: 'LMNOldSessionController'
        templateUrl: '/lmn_session:resources/partial/session.html'


angular.module('lmn.session').controller 'LMNOldSessionController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap, filesystem, validation, $rootScope, wait, userPassword) ->
    pageTitle.set(gettext('Session'))


    $scope.generateSessionMouseover = gettext('Regenerate this session')
    $scope.startGeneratedSessionMouseover = gettext('Start this session unchanged (may not be up to date)')
    $scope.generateRoomsessionMouseover = gettext('Start session containing all users in this room')


    $scope.currentSession = {
        name: ""
        comment: ""
    }


    $scope.checkboxModel = {
       value1 : false,
       value2 : true
    }

    $scope.visible = {
       participanttable : 'none',
       sessiontable : 'none',
       sessionname : 'none',
       mainpage: 'show',
    }


    $scope.info = {
        message : ''
    }

    $scope._ = {
            addParticipant: null,
            addClass: null
    }

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
        sessionname = $scope.currentSession.comment + "-" + $scope.currentSession.name
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
        for participant in $scope.participants
            tempparticipants.push(participant.sAMAccountName)

        $http.post('/api/lmn/websession/webConferences', {sessionname: $scope.currentSession.comment + "-" + $scope.currentSession.name, sessiontype: "private", sessionpassword: "", participants: tempparticipants}).then (resp) ->
            if resp.data["status"] is "SUCCESS"
                $scope.websessionID = resp.data["id"]
                $scope.websessionAttendeePW = resp.data["attendeepw"]
                $scope.websessionModeratorPW = resp.data["moderatorpw"]
                $http.post('/api/lmn/websession/startWebConference', {sessionname: $scope.currentSession.comment + "-" + $scope.currentSession.name, id: $scope.websessionID, attendeepw: $scope.websessionAttendeePW, moderatorpw: $scope.websessionModeratorPW}).then (resp) ->
                    if resp.data["returncode"] is "SUCCESS"
                        $http.post('/api/lmn/websession/joinWebConference', {id: $scope.websessionID, password: $scope.websessionModeratorPW, name: $scope.identity.profile.sn + ", " + $scope.identity.profile.givenName}).then (resp) ->
                            $scope.websessionIsRunning = true
                            window.open(resp.data, '_blank')
                    else
                        notify.error gettext('Cannot start websession! Try to reload page!')
                        console.log(resp.data)
            else
                notify.error gettext("Create session failed! Try again later!")

    # Websession part

    $scope.changeClass = (item, participant) ->
        id = participant['sAMAccountName']
        #console.log (id)
        #console.log (item)
        #console.log (id+'.'+item)

        if document.getElementById(id+'.'+item).className.match (/(?:^|\s)changed(?!\S)/)
            #$scope.participants[id]['changed'] = false
            document.getElementById(id+'.'+item).className = document.getElementById(id+'.'+item).className.replace( /(?:^|\s)changed(?!\S)/g , '' )
        else
            # get index of current participant in participantslist
            index = $scope.participants.indexOf(participant)
            if item == 'exammode'
                $scope.participants[index]['exammode-changed'] = true
                document.getElementById(id+'.'+item).className += " changed"
            else
                $scope.participants[index]['changed'] = true
                document.getElementById(id+'.'+item).className += " changed"

    $scope.resetClass = () ->
        result = document.getElementsByClassName("changed")
        while result.length
            result[0].className = result[0].className.replace( /(?:^|\s)changed(?!\S)/g , '' )
        return

    $scope.selectAll = (item) ->
        managementgroup = 'group_'+item
        if item is 'exammode'
            managementgroup = 'exammode_boolean'
        # console.log item
        # console.log $scope.participants
        if $scope.fields[item].checkboxStatus is true
            angular.forEach $scope.participants, (participant) ->
                if participant[managementgroup] is true
                    participant[managementgroup] = false
                    #$scope.changeClass(id+'.'+item, id)
                    $scope.changeClass(item, participant)
        else
            angular.forEach $scope.participants, (participant) ->
                if participant[managementgroup] is false
                    participant[managementgroup] = true
                    #$scope.changeClass(id+'.'+item, id)
                    $scope.changeClass(item, participant)
        return

    $scope.killSession = (session,comment) ->
        if session is ''
            messagebox.show(title: gettext('No Session selected'), text: gettext('You have to select a session first.'), positive: 'OK')
            return
        messagebox.show(text: gettext("Delete Session:  "+comment+" ?"), positive: gettext('Delete'), negative: gettext('Cancel')).then () ->
            wait.modal(gettext('Deleting session...'), 'spinner')
            $http.delete("/api/lmn/oldsession/sessions/#{session}").then (resp) ->
                $rootScope.$emit('updateWaiting', 'done')
                $scope.visible.sessionname = 'none'
                $scope.visible.participanttable = 'none'
                $scope.visible.mainpage = 'show'
                $scope.sessionLoaded = false
                $scope.info.message = ''
                $scope.getSessions()
                $scope.currentSession.name = ''
                notify.success(gettext(resp.data))

    $scope.newSession = () ->
        messagebox.prompt(gettext('Session Name'), '').then (msg) ->
            if not msg.value
                return
            testChar = validation.isValidLinboConf(msg.value)
            if testChar != true
                notify.error gettext(testChar)
                return
            $http.put("/api/lmn/oldsession/sessions/#{msg.value}", {}).then (resp) ->
                $scope.getSessions()
                notify.success gettext('Session Created')
                # Reset alle messages and information to show session table
                $scope.info.message = ''
                $scope.currentSession.name = ''
                $scope.currentSession.comment = ''
                $scope.sessionLoaded = false
                $scope.visible.participanttable = 'none'

    $scope.getSessions = () ->
        # TODO Figure out why this only works correctly if defined in this function (translation string etc.)
        # translationstrings
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
           wifiaccess:
              visible: true
              icon:"fa fa-wifi"
              title: gettext('Wifi-Access')
              checkboxAll: true
              checkboxStatus: false
           internetaccess:
              visible: true
              icon:"fa fa-globe"
              title: gettext('Internet-Access')
              checkboxAll: true
              checkboxStatus: false
           intranetaccess:
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
        #get groups
        $http.get('/api/lmn/groupmembership/schoolclasses').then (resp) ->
            $scope.classes = resp.data
            $scope.classes = $scope.classes.filter($scope.filterMembership(true))

        $http.get('/api/lmn/oldsession/sessions').then (resp) ->
            if resp.data.length is 0
                $scope.sessions = resp.data
                $scope.info.message = gettext("There are no sessions yet. Create a session using the 'New Session' button at the top!")
            else
                $scope.visible.sessiontable = 'show'
                $scope.sessions = resp.data

    $scope.filterMembership = (val) ->
            return (dict) ->
                dict['membership'] == val

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
        $http.get('/api/lmn/oldsession/userInRoom').then (resp) ->
            if resp.data == 0
                messagebox.show(title: gettext('Info'), text: gettext('Currenty its not possible to determine your room, try to login into your computer again.'), positive: 'OK')
            else
                usersInRoom=resp.data
                $uibModal.open(
                   templateUrl: '/lmn_session:resources/partial/roomDetails.modal.html'
                   controller:  'LMNOldRoomDetailsController'
                   size: 'lg'
                   resolve:
                     usersInRoom: () -> usersInRoom
                )

    $scope.renameSession = (session, comment) ->
        if session is ''
            messagebox.show(title: gettext('No Session selected'), text: gettext('You have to select a session first.'), positive: 'OK')
            return
        messagebox.prompt(gettext('Session Name'), comment).then (msg) ->
            if not msg.value
                return
            testChar = validation.isValidLinboConf(msg.value)
            if testChar != true
                notify.error gettext(testChar)
                return
            $http.post('/api/lmn/oldsession/sessions', {action: 'rename-session', session: session, comment: msg.value}).then (resp) ->
                $scope.getSessions()
                $scope.currentSession.name = ''
                $scope.sessionLoaded = false
                $scope.currentSession.comment = ''
                $scope.visible.sessiontable = 'none'
                $scope.visible.participanttable = 'none'
                $scope.info.message = ''
                notify.success gettext('Session Renamed')

    $scope.getParticipants = (session) ->
        $scope.visible.sessiontable = 'none'
        $scope.resetClass()
        # Reset select all checkboxes when loading participants
        angular.forEach $scope.fields, (field) ->
            field.checkboxStatus = false
        $http.get("/api/lmn/oldsession/sessions/#{session}").then (resp) ->
            $scope.visible.sessionname = 'show'
            $scope.sessionLoaded = 'true'
            $scope.filter = ''
            $scope.visible.mainpage = 'none'
            $scope.participants = resp.data
            if $scope.participants == 'empty'
               $scope.visible.participanttable = 'none'
               $scope.info.message = gettext('This session appears to be empty. Start adding users by using the top search bar!')
            else
                $scope.info.message = ''
                $scope.visible.participanttable = 'show'

    $scope.findUsers = (q) ->
        return $http.get("/api/lmn/oldsession/user-search/#{q}").then (resp) ->
            $scope.users = resp.data
            return resp.data

    $scope.findSchoolClasses = (q) ->
        return $http.get("/api/lmn/oldsession/schoolClass-search/#{q}").then (resp) ->
            $scope.class = resp.data
            return resp.data


    $scope.loadGeneratedSession = (classname) ->
        sessionComment = classname+'-autoGenerated'
        sessionExist=false
        for session in $scope.sessions
            if sessionComment == session['COMMENT']
                sessionExist=true
                sessionID= session['ID']
                console.log ('sessionExist '+sessionExist )
        if sessionExist == false
            $scope.regenerateSession(classname)
        if sessionExist == true
            # open existing session
            $scope.currentSession.name=sessionID
            $scope.currentSession.comment=sessionComment
            $scope.getParticipants(sessionID)
            $scope.getWebConferenceEnabled()

    $scope.generateRoomSession = () ->
        $http.get('/api/lmn/oldsession/userInRoom').then (resp) ->
            if resp.data == 0
                messagebox.show(title: gettext('Info'), text: gettext('Currenty its not possible to determine your room, try to login into your computer again.'), positive: 'OK')
            else
                usersInRoom=resp.data.usersList
                sessionComment = 'room-autoGenerated'
                sessionExist=false
                for session in $scope.sessions
                    if sessionComment == session['COMMENT']
                        sessionExist=true
                        sessionID= session['ID']
                        console.log ('sessionExist '+sessionExist )
                wait.modal(gettext('Generating session...'), 'spinner')
                $scope.generateSession(usersInRoom, sessionID, sessionComment, sessionExist)

    $scope.regenerateSession = (classname) ->
        sessionComment = classname+'-autoGenerated'
        sessionExist=false
        for session in $scope.sessions
            if sessionComment == session['COMMENT']
                sessionExist=true
                sessionID= session['ID']
                console.log ('sessionExist '+sessionExist )

        wait.modal(gettext('Generating session...'), 'spinner')
        $http.get('/api/lmn/groupmembership/groups/' + classname).then (resp) ->
            # get participants from specified class
            participants = resp.data['MEMBERS'][classname]
            participantsArray = []
            for participant,data of participants
                if participants[participant]['sophomorixRole'] != 'teacher'
                    participantsArray.push participant
            #$rootScope.$emit('updateWaiting', 'done')
            $scope.generateSession(participantsArray, sessionID, sessionComment, sessionExist)

    $scope.generateSession =  (participants,sessionID, sessionComment, sessionExist) ->
        #wait.modal(gettext('Generating session...'), 'spinner')
        # fix existing session
        if sessionExist == true
            $http.post('/api/lmn/oldsession/sessions', {action: 'update-session', username: $scope.identity.user, sessionID: sessionID, participants: participants}).then (resp) ->
                # emit wait process is done
                $rootScope.$emit('updateWaiting', 'done')
                # refresh Session table
                notify.success gettext('Session generated')
                # open new created session
                $scope.currentSession.name=sessionID
                $scope.currentSession.comment=sessionComment
                $scope.getParticipants(sessionID)
                $scope.getWebConferenceEnabled()
        # create new session
        if sessionExist == false
            # create new specified session
            $http.put("/api/lmn/oldsession/sessions/#{sessionComment}", {participants: participants}).then (resp) ->
                # emit wait process is done
                $rootScope.$emit('updateWaiting', 'done')
                await $scope.getSessions()
                notify.success gettext('Session generated')
                # get new created sessionID
                for session in $scope.sessions
                    if sessionComment == session['COMMENT']
                        sessionID= session['ID']
                # open new created session
                $scope.currentSession.name=sessionID
                $scope.currentSession.comment=sessionComment
                $scope.getParticipants(sessionID)
                $scope.getWebConferenceEnabled()


    $scope.$watch '_.addParticipant', () ->
                # console.log $scope._.addParticipant
                if $scope._.addParticipant
                    if $scope.participants == 'empty'
                                $scope.participants = []
                    $scope.info.message = ''
                    $scope.visible.participanttable = 'show'
                    #console.log $scope._.addParticipant
                    if $scope._.addParticipant.sophomorixRole is 'student'
                        # Add Managementgroups list if missing. This happens when all managementgroup attributes are false, causing the json tree to skip this key
                        if not $scope._.addParticipant.MANAGEMENTGROUPS?
                                    $scope._.addParticipant.MANAGEMENTGROUPS = []
                        #if not $scope._.addParticipant.changed?
                        #            $scope._.addParticipant.changed = 'False'
                        #if not $scope._.addParticipant.exammode-changed?
                        #            $scope._.addParticipant.exammode-changed = 'False'
                        $scope.participants.push {"sAMAccountName":$scope._.addParticipant.sAMAccountName,"givenName":$scope._.addParticipant.givenName,"sn":$scope._.addParticipant.sn,
                        "sophomorixExamMode":$scope._.addParticipant.sophomorixExamMode || '---',
                        "group_webfilter":$scope._.addParticipant.MANAGEMENTGROUPS.webfilter,
                        "group_intranetaccess":$scope._.addParticipant.MANAGEMENTGROUPS.intranet,
                        "group_printing":$scope._.addParticipant.MANAGEMENTGROUPS.printing,
                        "sophomorixStatus":"U","sophomorixRole":$scope._.addParticipant.sophomorixRole,
                        "group_internetaccess":$scope._.addParticipant.MANAGEMENTGROUPS.internet,
                        "sophomorixAdminClass":$scope._.addParticipant.sophomorixAdminClass,
                        "user_existing":true,"group_wifiaccess":$scope._.addParticipant.MANAGEMENTGROUPS.wifi,
                        "changed": false, "exammode-changed": false, "exammode_boolean":false}
                    # console.log ($scope.participants)
                    $scope._.addParticipant = null

    # TODO Figure out how to call the existing watch addParticipant function
    $scope.addParticipant = (participant) ->
        if participant
            if $scope.participants == 'empty'
                        $scope.participants = []
            $scope.info.message = ''
            $scope.visible.participanttable = 'show'
            # console.log participant
            # Only add Students
            if participant.sophomorixRole is 'student'
                # Add Managementgroups list if missing. This happens when all managementgroup attributes are false, causing the json tree to skip this key
                if not participant.MANAGEMENTGROUPS?
                            participant.MANAGEMENTGROUPS = []
                #if not participant.changed?
                #            participant.changed = 'False'
                #if not participant.exammode-changed?
                #            participant.exammode-changed = 'False'
                # console.log ($scope.participants)
                $scope.participants.push {"sAMAccountName":participant.sAMAccountName,"givenName":participant.givenName,"sn":participant.sn,
                "sophomorixExamMode":participant.sophomorixExamMode,
                "group_webfilter":participant.MANAGEMENTGROUPS.webfilter,
                "group_intranetaccess":participant.MANAGEMENTGROUPS.intranet,
                "group_printing":participant.MANAGEMENTGROUPS.printing,
                "sophomorixStatus":"U","sophomorixRole":participant.sophomorixRole,
                "group_internetaccess":participant.MANAGEMENTGROUPS.internet,
                "sophomorixAdminClass":participant.sophomorixAdminClass,
                "user_existing":true,"group_wifiaccess":participant.MANAGEMENTGROUPS.wifi,
                "changed": false, "exammode-changed": false}
            participant = null

    $scope.$watch '_.addSchoolClass', () ->
        if $scope._.addSchoolClass
            members = $scope._.addSchoolClass.members
            for schoolClass,member of $scope._.addSchoolClass.members
                $scope.addParticipant(member)
            $scope._.addSchoolClass = null

    $scope.removeParticipant = (participant) ->
        deleteIndex = $scope.participants.indexOf(participant)
        if deleteIndex != -1
            $scope.participants.splice(deleteIndex, 1)

    $scope.changeExamSupervisor = (participant, supervisor) ->
        $http.post('/api/lmn/oldsession/sessions', {action: 'change-exam-supervisor', supervisor: supervisor, participant: participant}).then (resp) ->

    $scope.endExam = (participant, supervisor,session, sessionName) ->
        $http.patch("/api/lmn/oldsession/exam/#{sessionName}", {supervisor: supervisor, participant: participant}).then (resp) ->
            $scope.getParticipants(session)

    $scope.saveApply = (username,participants, session, sessionName) ->
        wait.modal(gettext('Changes are applied...'), 'progressbar')
        $http.post('/api/lmn/oldsession/sessions', {action: 'save-session',username: username, participants: participants, session: session, sessionName: sessionName}).then (resp) ->
            # emit process is done
            $rootScope.$emit('updateWaiting', 'done')
            $scope.output = resp.data
            $scope.getParticipants(session)
            notify.success gettext($scope.output)

    $scope.cancel = (username,participants, session) ->
        $scope.getSessions()
        $scope.sessionLoaded = false
        $scope.info.message = ''
        $scope.participants = ''
        $scope.currentSession.name = ''
        $scope.currentSession.comment = ''
        $scope.visible.participanttable = 'none'

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
        console.log (user)
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
           templateUrl: '/lmn_session:resources/partial/selectFile.modal.html'
           controller: 'LMNOldSessionFileSelectModalController'
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
               $http.post('/api/lmn/oldsession/trans', {command: command, senders: senders, receivers: receivers, files: result.files, session: sessioncomment}).then (resp) ->
                   $rootScope.$emit('updateWaiting', 'done')
                   console.log (resp)
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
           templateUrl: '/lmn_session:resources/partial/selectFile.modal.html'
           controller: 'LMNOldSessionFileSelectModalController'
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
                    $http.post('/api/lmn/oldsession/trans', {command: command, senders: senders, receivers: receivers, files: result.files, session: sessioncomment}).then (resp) ->
                        $rootScope.$emit('updateWaiting', 'done')
                        validateResult(resp)
                if command is 'move'
                    $http.post('/api/lmn/oldsession/trans', {command: command, senders: senders, receivers: receivers, files: result.files, session: sessioncomment}).then (resp) ->
                        $rootScope.$emit('updateWaiting', 'done')
                        validateResult(resp)


    $scope.notImplemented = (user) ->
                messagebox.show(title: gettext('Not implemented'), positive: 'OK')

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
            return
        if $scope.identity.user is null
            return
        if $scope.identity.user is 'root'
            return
        $scope.getSessions()

angular.module('lmn.session').controller 'LMNOldRoomDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, usersInRoom) ->
        $scope.usersInRoom = usersInRoom

        $scope.close = () ->
            $uibModalInstance.dismiss()
