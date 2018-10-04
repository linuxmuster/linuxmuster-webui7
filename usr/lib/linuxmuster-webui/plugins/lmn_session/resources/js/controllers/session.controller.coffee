angular.module('lmn.session').controller 'LMNSessionFileSelectModalController', ($scope, $uibModalInstance, gettext, notify, $http, bulkMode, senders, receivers, action, command) ->
    $scope.bulkMode = bulkMode
    $scope.senders = senders
    $scope.receivers = receivers
    $scope.action = action
    $scope.command = command


    if bulkMode is 'false'
        $http.post('/api/lmn/session/trans-list-files', {user: senders[0]}).then (resp) ->
            $scope.files = resp['data'][0]
            $scope.filesList = resp['data'][1]
    else
        if action is 'share'
            $http.post('/api/lmn/session/trans-list-files', {user: senders[0]}).then (resp) ->
                $scope.files = resp['data'][0]
                $scope.filesList = resp['data'][1]

    $scope.save = () ->
        filesToTrans =  []
        angular.forEach $scope.files['TREE'], (file, id) ->
            if file['checked'] is true
                filesToTrans.push(id)
        console.log (filesToTrans)
        $uibModalInstance.close(response: 'accept', files: filesToTrans)

    $scope.close = () ->
        $uibModalInstance.dismiss()




angular.module('lmn.session').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/session',
        controller: 'LMNSessionController'
        templateUrl: '/lmn_session:resources/partial/session.html'


angular.module('lmn.session').controller 'LMNSessionController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap, filesystem) ->
    pageTitle.set(gettext('Session'))

    $scope.currentSession = {
        name: ""
        comment: ""
    }

    $scope.sorts = [
       {
          name: gettext('Login name')
          fx: (x) -> x.sAMAccountName
       }
       {
          name: gettext('Lastname')
          fx: (x) -> x.sn
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

    $scope.checkboxModel = {
       value1 : false,
       value2 : true
    }

    $scope.visible = {
       participanttable : 'none',
       sessiontable : 'none',
       sessionname : 'none',
       mainpage: 'show'
    }


    $scope.info = {
        message : ''
    }

    $scope._ = {
            addParticipant: null,
            addClass: null
    }

    $scope.changeClass = (item, id) ->
        #console.log (id)
        #console.log (item)

        if document.getElementById(id+'.'+item).className.match (/(?:^|\s)changed(?!\S)/)
            #$scope.participants[id]['changed'] = false
            document.getElementById(id+'.'+item).className = document.getElementById(id+'.'+item).className.replace( /(?:^|\s)changed(?!\S)/g , '' )
        else
            if item == 'exammode'
                $scope.participants[id]['exammode-changed'] = true
                document.getElementById(id+'.'+item).className += " changed"
            else
                $scope.participants[id]['changed'] = true
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
        #console.log item
        #console.log $scope.participants
        if $scope.fields[item].checkboxStatus is true
            angular.forEach $scope.participants, (participant, id) ->
                if participant[managementgroup] is true
                    participant[managementgroup] = false
                    #$scope.changeClass(id+'.'+item, id)
                    $scope.changeClass(item, id)
        else
            angular.forEach $scope.participants, (participant,id) ->
                if participant[managementgroup] is false
                    participant[managementgroup] = true
                    #$scope.changeClass(id+'.'+item, id)
                    $scope.changeClass(item, id)
        return

    $scope.killSession = (username,session,comment) ->
                if session is ''
                    messagebox.show(title: gettext('No Session selected'), text: gettext('You have to select a session first.'), positive: 'OK')
                    return
                messagebox.show(text: "Delete '#{comment}'?", positive: 'Delete', negative: 'Cancel').then () ->
                    $http.post('/api/lmn/session/sessions', {action: 'kill-sessions', session: session}).then (resp) ->
                        #notify.success gettext('Session Deleted')
                        $scope.visible.sessionname = 'none'
                        $scope.visible.participanttable = 'none'
                        $scope.visible.mainpage = 'show'
                        $scope.info.message = ''
                        $scope.getSessions($scope.identity.user)
                        $scope.currentSession.name = ''
                        notify.success gettext(resp.data)

    $scope.newSession = (username) ->
                messagebox.prompt(gettext('Session Name'), '---').then (msg) ->
                    if not msg.value
                        return
                    $http.post('/api/lmn/session/sessions', {action: 'new-session', username: username, comment: msg.value}).then (resp) ->
                        $scope.new-sessions = resp.data
                        $scope.getSessions($scope.identity.user)
                        notify.success gettext('Session Created')
                        # Reset alle messages and information to show session table
                        $scope.info.message = ''
                        $scope.currentSession.name = ''
                        $scope.currentSession.comment = ''
                        $scope.visible.participanttable = 'none'


    $scope.getSessions = (username) ->
                $http.post('/api/lmn/session/sessions', {action: 'get-sessions', username: username}).then (resp) ->
                    if resp.data[0]['SESSIONCOUNT'] is 0
                        $scope.sessions = resp.data
                        $scope.info.message = gettext('There are no sessions yet. Create a session using the "Edit Sessions" button at the top!')
                        console.log ('no sessions')
                    else
                        console.log ('sessions found')
                        $scope.visible.sessiontable = 'show'
                        $scope.sessions = resp.data


    $scope.renameSession = (username, session, comment) ->
                if session is ''
                    messagebox.show(title: gettext('No Session selected'), text: gettext('You have to select a session first.'), positive: 'OK')
                    return
                messagebox.prompt(gettext('Session Name'), comment).then (msg) ->
                    if not msg.value
                        return
                    $http.post('/api/lmn/session/sessions', {action: 'rename-session', session: session, comment: msg.value}).then (resp) ->
                        $scope.getSessions($scope.identity.user)
                        notify.success gettext('Session Renamed')

    $scope.getParticipants = (username,session) ->
                $scope.visible.sessiontable = 'none'
                $scope.resetClass()
                # Reset select all checkboxes when loading participants
                angular.forEach $scope.fields, (field) ->
                    field.checkboxStatus = false
                $http.post('/api/lmn/session/sessions', {action: 'get-participants', username: username, session: session}).then (resp) ->
                    $scope.visible.sessionname = 'show'
                    $scope.visible.mainpage = 'none'
                    $scope.participants = resp.data
                    if $scope.participants[0]?
                       $scope.visible.participanttable = 'none'
                       $scope.info.message = gettext('This session appears to be empty. Start adding users by using the top search bar!')
                    else
                        $scope.info.message = ''
                        $scope.visible.participanttable = 'show'

    $scope.findUsers = (q) ->
                return $http.get("/api/lmn/session/user-search?q=#{q}").then (resp) ->
                            $scope.users = resp.data
                            #console.log resp.data
                            return resp.data

    $scope.findSchoolClasses = (q) ->
                return $http.get("/api/lmn/session/schoolClass-search?q=#{q}").then (resp) ->
                            $scope.class = resp.data
                            #console.log resp.data
                            return resp.data

    $scope.$watch '_.addParticipant', () ->
                # console.log $scope._.addParticipant
                if $scope._.addParticipant
                    if $scope.participants[0]?
                                delete $scope.participants['0']
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

                        $scope.participants[$scope._.addParticipant.sAMAccountName] = angular.copy({"givenName":$scope._.addParticipant.givenName,"sn":$scope._.addParticipant.sn,
                        "sophomorixExamMode":$scope._.addParticipant.sophomorixExamMode,
                        "group_webfilter":$scope._.addParticipant.MANAGEMENTGROUPS.webfilter,
                        "group_intranetaccess":$scope._.addParticipant.MANAGEMENTGROUPS.intranet,
                        "group_printing":$scope._.addParticipant.MANAGEMENTGROUPS.printing,
                        "sophomorixStatus":"U","sophomorixRole":$scope._.addParticipant.sophomorixRole,
                        "group_internetaccess":$scope._.addParticipant.MANAGEMENTGROUPS.internet,
                        "sophomorixAdminClass":$scope._.addParticipant.sophomorixAdminClass,
                        "user_existing":true,"group_wifiaccess":$scope._.addParticipant.MANAGEMENTGROUPS.wifi,
                        "changed": false, "exammode-changed": false})
                    $scope._.addParticipant = null

    # TODO Figure out how to call the existing watch addParticipant function
    $scope.addParticipant = (participant) ->
                if participant
                    if $scope.participants[0]?
                                delete $scope.participants['0']
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
                        $scope.participants[participant.sAMAccountName] = angular.copy({"givenName":participant.givenName,"sn":participant.sn,
                        "sophomorixExamMode":participant.sophomorixExamMode,
                        "group_webfilter":participant.MANAGEMENTGROUPS.webfilter,
                        "group_intranetaccess":participant.MANAGEMENTGROUPS.intranet,
                        "group_printing":participant.MANAGEMENTGROUPS.printing,
                        "sophomorixStatus":"U","sophomorixRole":participant.sophomorixRole,
                        "group_internetaccess":participant.MANAGEMENTGROUPS.internet,
                        "sophomorixAdminClass":participant.sophomorixAdminClass,
                        "user_existing":true,"group_wifiaccess":participant.MANAGEMENTGROUPS.wifi,
                        "changed": false, "exammode-changed": false})
                    participant = null

    $scope.$watch '_.addSchoolClass', () ->
                if $scope._.addSchoolClass
                    members = $scope._.addSchoolClass.members
                    for schoolClass,member of $scope._.addSchoolClass.members
                        $scope.addParticipant(member)
                    $scope._.addSchoolClass = null

    $scope.removeParticipant = (participant) ->
                delete $scope.participants[participant]

    $scope.changeExamSupervisor = (participant, supervisor) ->
                $http.post('/api/lmn/session/sessions', {action: 'change-exam-supervisor', supervisor: supervisor, participant: participant}).then (resp) ->

    $scope.saveApply = (username,participants, session) ->
                console.log (participants)
                $http.post('/api/lmn/session/sessions', {action: 'save-session',username: username, participants: participants, session: session}).then (resp) ->
                    $scope.output = resp.data
                    $scope.getParticipants(username,session)
                    notify.success gettext($scope.output)

    $scope.cancel = (username,participants, session) ->
        $scope.getSessions($scope.identity.user)
        $scope.info.message = ''
        $scope.currentSession.name = ''
        $scope.currentSession.comment = ''
        $scope.visible.participanttable = 'none'

    $scope.showInitialPassword = (user) ->
                $http.post('/api/lm/users/password', {users: user, action: 'get'}).then (resp) ->
                    messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')

    $scope.setInitialPassword = (user) ->
                $http.post('/api/lm/users/password', {users: user, action: 'set-initial'}).then (resp) ->
                    notify.success gettext('Initial password set')

    $scope.setRandomPassword = (user) ->
            $http.post('/api/lm/users/password', {users: user, action: 'set-random'}).then (resp) ->
                notify.success gettext('Random password set')

    $scope.setCustomPassword = (user) ->
        $uibModal.open(
            templateUrl: '/lm_users:resources/partial/customPassword.modal.html'
            controller: 'LMNUsersCustomPasswordController'
            size: 'mg'
            resolve:
                users: () -> user
        )

    $scope.userInfo = (user) ->
        $uibModal.open(
            templateUrl: '/lm_users:resources/partial/userDetails.modal.html'
            controller: 'LMNUserDetailsController'
            size: 'lg'
            resolve:
                id: () -> user
                role: () -> 'students'
        )


    typeIsArray = Array.isArray || ( value ) -> return {}.toString.call( value ) is '[object Array]'

    $scope.shareTrans = (command, senders, receivers) ->
        # if share with session we get the whole session as a json object.
        # The function on the other hand waits for an array so we extract
        # the username into an array
        bulkMode = 'false'
        if not typeIsArray receivers
            bulkMode = 'true'
            participantsArray = []
            for key, value of receivers
                participantsArray.push key
            receivers = participantsArray
        $uibModal.open(
           templateUrl: '/lmn_session:resources/partial/selectFile.modal.html'
           controller: 'LMNSessionFileSelectModalController'
           resolve:
              action: () -> 'share'
              bulkMode: () -> bulkMode
              senders: () -> senders
              receivers: () -> receivers
              command: () -> command
        ).result.then (result) ->
           if result.response is 'accept'
               $http.post('/api/lmn/session/trans', {command: command, senders: senders, receivers: receivers, files: result.files}).then (resp) ->

        ##messagebox.show(title: gettext('Share Data'),text: gettext("Share EVERYTHING in transfer folder to user(s) '#{receivers}'?"), positive: gettext('Proceed'), negative: gettext('Cancel')).then () ->
        ##    $http.post('/api/lmn/session/trans', {command: command, senders: senders, receivers: receivers}).then (resp) ->
        ##        notify.success gettext('success')

    $scope.collectTrans = (command, senders, receivers) ->
        bulkMode = 'false'
        if not typeIsArray senders
            bulkMode = 'true'
            participantsArray = []
            for key, value of senders
                participantsArray.push key
            senders = participantsArray
        transTitle = 'transfer'
        $uibModal.open(
           templateUrl: '/lmn_session:resources/partial/selectFile.modal.html'
           controller: 'LMNSessionFileSelectModalController'
           resolve:
              action: () -> 'collect'
              bulkMode: () -> bulkMode
              senders: () -> senders
              receivers: () -> receivers
              command: () -> command
        ).result.then (result) ->
            if result.response is 'accept'
                return
                if command is 'copy'
                    #messagebox.show(title: gettext('Copy Data'),text: gettext("Copy '#{{result.files}}' from transfer folder of these user(s) '#{senders}'? All files are still available in users transfer directory!"), positive: gettext('Proceed'), negative: gettext('Cancel')).then () ->
                    $http.post('/api/lmn/session/trans', {command: command, senders: senders, receivers: receivers}).then (resp) ->
                        notify.success gettext('success')
                if command is 'move'
                    #messagebox.show(title: gettext('Collect Data'),text: gettext("Collect '#{{result.files}}' from transfer folder of these user(s) '#{senders}'? No files will be available by the users!"), positive: gettext('Proceed'), negative: gettext('Cancel')).then () ->
                    $http.post('/api/lmn/session/trans', {command: command, senders: senders, receivers: receivers}).then (resp) ->
                        notify.success gettext('success')



            #if command is 'copy'
            #            messagebox.show(title: gettext('Copy Data'),text: gettext("Copy EVERYTHING from transfer folder of these user(s) '#{senders}'? All files are still available in users transfer directory!"), positive: gettext('Proceed'), negative: gettext('Cancel')).then () ->
            #                $http.post('/api/lmn/session/trans', {command: command, senders: senders, receivers: receivers}).then (resp) ->
            #                    notify.success gettext('success')
            #        if command is 'move'
            #            messagebox.show(title: gettext('Collect Data'),text: gettext("Collevt EVERYTHING from transfer folder of these user(s) '#{senders}'? No files will be available by the users!"), positive: gettext('Proceed'), negative: gettext('Cancel')).then () ->
            #                $http.post('/api/lmn/session/trans', {command: command, senders: senders, receivers: receivers}).then (resp) ->
            #                    notify.success gettext('success')
            #
    $scope.notImplemented = (user) ->
                messagebox.show(title: gettext('Not implemented'), positive: 'OK')

    $scope.$watch 'identity.user', ->
          console.log ($scope.identity.user)
          if $scope.identity.user is undefined
              return
          if $scope.identity.user is null
              return
          if $scope.identity.user is 'root'
              # $scope.identity.user = 'hulk'
              return
          $scope.getSessions($scope.identity.user)
          return

