angular.module('lmn.websession').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/websession',
        controller: 'LMNWebsessionController'
        templateUrl: '/lmn_websession:resources/partial/index.html'


angular.module('lmn.websession').controller 'LMNWebsessionController', ($rootScope, $scope, $window, $http, $uibModal, $location, gettext, notify, pageTitle, messagebox) ->
    pageTitle.set(gettext('Websession'))

    $scope.getWebConferenceEnabled = () ->
        $http.get('/api/lmn/websession/webConferenceEnabled').then (resp) ->
            if resp.data == true
                $scope.enabled = true
                $scope.getWebConferences()
            else
                $scope.enabled = false;

    $scope.getWebConferences = () ->
        $http.get('/api/lmn/websession/webConferences').then (resp) ->
            $scope.myWebsessions = resp.data

    $scope.createWebsession = () ->
        $uibModal.open(
            templateUrl: '/lmn_websession:resources/partial/createSession.modal.html'
            controller:  'LMNCreateWebsessionModalController'
            size: 'mg'
        ).result.then (result) ->
            $scope.refreshSessionList()
            notify.success gettext('Created successfully!')
    
    $scope.startWebsession = (sessionname, id, attendeepw, moderatorpw) ->
        $http.post('/api/lmn/websession/startWebConference', {sessionname: sessionname, id: id, attendeepw: attendeepw, moderatorpw: moderatorpw}).then (resp) ->
            if resp.data["returncode"] is "SUCCESS"
                $http.post('/api/lmn/websession/joinWebConference', {id: id, password: moderatorpw, name: $scope.identity.profile.sn + ", " + $scope.identity.profile.givenName}).then (resp) ->
                    $scope.refreshSessionList()
                    window.open(resp.data, '_blank')
            else
                notify.error gettext('Cannot start websession! Try to reload page!')
                console.log(resp.data)

    $scope.joinWebsession = (id, password) ->
        $http.post('/api/lmn/websession/joinWebConference', {id: id, password: password, name: $scope.identity.profile.sn + ", " + $scope.identity.profile.givenName}).then (resp) ->
            $scope.refreshSessionList()
            window.open(resp.data, '_blank')

    $scope.endWebsession = (id, moderatorpw) ->
        $http.post('/api/lmn/websession/endWebConference', {id: id, moderatorpw: moderatorpw}).then (resp) ->
            if resp.data["returncode"] is "SUCCESS"
                $scope.refreshSessionList()
                notify.success gettext('Stopped successfully!')
            else
                notify.error gettext('Cannot stop websession! Try to reload page!')
                console.log(resp.data)

    $scope.deleteWebsession = (id) ->
        messagebox.show(text: "Delete #{id}?", positive: 'Delete', negative: 'Cancel').then () ->
            $http.delete("/api/lmn/websession/webConference/#{$scope.websessionID}").then (resp) ->
                $scope.refreshSessionList()
                if resp.data["status"] == "SUCCESS"
                    notify.success gettext("Successfully removed!")
                else
                    notify.error gettext('Cannot delete entry!')

    $scope.copyURL = (id) ->
        url = window.location.href.split("/")
        url = url[0] + "//" + url[2] + "/websession/" + id
        copyElement = document.createElement("textarea")
        copyElement.textContent = url
        body = document.getElementsByTagName('body')[0]
        body.appendChild(copyElement)
        copyElement.select()
        document.execCommand('copy')
        body.removeChild(copyElement)
        notify.success gettext('Copied!')
        return true

    $scope.showURL = (id) ->
        url = window.location.href.split("/")
        url = url[0] + "//" + url[2] + "/websession/" + id
        messagebox.show(text: url, positive: 'Ok')

    $scope.showParticipants = (participants) ->
        $uibModal.open(
            template: '<div class="modal-header"><h4 translate>Participants</h4></div>
            <div class="modal-body"><table class="table table-hover"><tr ng:repeat="participant in participants"><td>{{participant}}</td></tr></table></div>'
            controller: 'LMNShowParticipantsModalController'
            resolve:
                participants: () -> participants
        )

    $scope.refreshSessionList = () ->
        $scope.getWebConferences()

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
           return
        if $scope.identity.user is null
           return
        if $scope.identity.user is 'root'
           return

        $scope.user = $scope.identity.profile
        $scope.getWebConferenceEnabled()

angular.module('lmn.websession').controller 'LMNShowParticipantsModalController', ($scope, $window, $route, $uibModal, $uibModalInstance, $http, participants) ->
    $scope.participants = participants

angular.module('lmn.websession').controller 'LMNCreateWebsessionModalController', ($scope, $window, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle) ->
    pageTitle.set(gettext('Websession'))

    $scope.sessionname = ""
    $scope.sessiontype = "public"
    $scope.sessionpassword = ""

    $scope._ = {
        addParticipant: null,
        addClass: null
    }

    $scope.participants = []
    
    $scope.create = () ->
        if not $scope.sessionname
            notify.error gettext("You have to enter a name!")
            return

        tempparticipants = []
        for participant in $scope.participants
            tempparticipants.push(participant.sAMAccountName)

        $http.post('/api/lmn/websession/webConferences', {sessionname: $scope.sessionname, sessiontype: $scope.sessiontype, sessionpassword: $scope.sessionpassword, participants: tempparticipants}).then (resp) ->
            if resp.data["status"] != "SUCCESS"
                notify.error gettext("Create session failed! Try again later!")
            $uibModalInstance.dismiss()

    $scope.findUsers = (q) ->
        return $http.gett("/api/lmn/session/user-search/#{q}").then (resp) ->
            $scope.users = resp.data
            return resp.data

    $scope.findSchoolClasses = (q) ->
        return $http.get("/api/lmn/session/schoolClass-search/#{q}").then (resp) ->
            $scope.class = resp.data
            return resp.data

    $scope.$watch '_.addParticipant', () ->
        if $scope._.addParticipant
            $scope.participants.push($scope._.addParticipant)
            $scope._.addParticipant = null
    
    $scope.$watch '_.addSchoolClass', () ->
        if $scope._.addSchoolClass
            members = $scope._.addSchoolClass.members
            for schoolClass,member of $scope._.addSchoolClass.members
                $scope.addParticipant(member)
            $scope._.addSchoolClass = null

    $scope.addParticipant = (participant) ->
        $scope.participants.push(participant)

    $scope.removeParticipant = (participant) ->
        deleteIndex = $scope.participants.indexOf(participant)
        if deleteIndex != -1
            $scope.participants.splice(deleteIndex, 1)

    $scope.close = () ->
        $uibModalInstance.dismiss()
