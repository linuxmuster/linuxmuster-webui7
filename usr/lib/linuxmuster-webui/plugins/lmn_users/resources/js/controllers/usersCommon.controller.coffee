angular.module('lm.users').controller 'LMNUsersCustomPasswordController', ($scope, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, users, type, validation) ->
    $scope.username = users
    $scope.action = type

    $scope.save = (userpw) ->
        if not type?
            action = 'set'
        else
            if type == 'actual'
                action = 'set-actual'
            else
                action = 'set'

        if not $scope.userpw
            notify.error gettext("You have to enter a password")
            return

        test = validation.isValidPassword($scope.userpw)
        if test != true
           notify.error gettext(test)
           return
        else
            $http.post('/api/lm/users/password', {users: (x['sAMAccountName'] for x in users), action: action, password: $scope.userpw, type: type}).then (resp) ->
                notify.success gettext('New password set')
        $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()

angular.module('lm.users').controller 'LMNUserDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, id, role) ->

    #notify.error gettext("You have to enter a username")
    $scope.id = id
    $scope.showGroupDetails = true
    $scope.nevertext = gettext('Never')

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

    $scope.hidetext = gettext("Hide")
    $scope.showtext = gettext("Show")

    $http.post('/api/lm/sophomorixUsers/'+role, {action: 'get-specified', user: id}).then (resp) ->
        $scope.userDetails = resp.data
        $scope.groups = []
        for dn in $scope.userDetails[0]['memberOf']
            cn       = dn.split(',')[0].split('=')[1]
            category = dn.split(',')[1].split('=')[1]
            $scope.groups.push({'cn':cn, 'category':category})

        console.log ($scope.userDetails)

    $scope.close = () ->
        $uibModalInstance.dismiss()



angular.module('lm.users').controller 'LMUsersSortListModalController', ($scope, $window, $http, $uibModalInstance, messagebox, notify, $uibModal, gettext, filesystem, userlist, userListCSV) ->


    $scope.userListCSV = userListCSV
    $scope.userlist = userlist

    $scope.rebuildCSV = () ->
        # add empty 'not used' fields if CSV contains more coloumns than fields
        while $scope['userListCSV'].length > $scope['coloumnTitles'].length
            $scope['coloumnTitles'].push({name: gettext('not used')})

        i = 0
        for element in $scope.userListCSV
            element.coloumn = $scope.coloumnTitles[i]['id']
            i = i + 1
        #console.log ($scope['userListCSV'])


    $scope.togglecustomField = (field) ->
        # get index of field in coloumnTitles (-1 if not presend)
        pos = $scope.coloumnTitles.map((e) ->
              e.name
        ).indexOf(field)

        # add field if not presend
        if pos  == -1
            $scope.coloumnTitles.splice(4, 0, {name: field, id: field})
        # splice this field 
        else
            $scope.coloumnTitles.splice(pos, 1)
        $scope.rebuildCSV()


    $scope.accept = () ->
        #console.log ($scope.userListCSV)
        $uibModalInstance.close($scope.userListCSV)

    $scope.close = () ->
        $uibModalInstance.dismiss()

    if userlist == 'students.csv'
        $scope.coloumnTitles = [
            {name: gettext('class'), id: 'class'}
            {name: gettext('lastname'), id: 'lastname'}
            {name: gettext('firstname'), id: 'firstname'}
            {name: gettext('birthday'), id: 'birthday'}
        ]

    if userlist == 'teachers.csv'
        $scope.coloumnTitles = [
            {name: gettext('lastname'), id: 'lastname'}
            {name: gettext('firstname'), id: 'firstname'}
            {name: gettext('birthday'), id: 'birthday'}
            {name: gettext('login'), id: 'login'}
        ]

    $scope.rebuildCSV()

angular.module('lm.users').controller 'LMUsersUploadModalController', ($scope, $window, $http, $uibModalInstance, messagebox, notify, $uibModal, gettext, filesystem, userlist) ->
    $scope.path = "/tmp/"
    $scope.onUploadBegin = ($flow) ->
        $uibModalInstance.close()
        msg = messagebox.show({progress: true})
        filesystem.startFlowUpload($flow, $scope.path).then(() ->
            notify.success(gettext('Uploaded'))
            filename = $flow["files"][0]["name"]
            $http.post('/api/lmn/sophomorixUsers/import-list', {action: 'get', path: $scope.path+filename, userlist: userlist}).then (resp) ->
                userListCSV = resp.data
                #console.log (userListCSV)
                # console.log (resp['data'])
                $uibModal.open(
                             templateUrl: '/lmn_users:resources/partial/sortList.modal.html'
                             controller: 'LMUsersSortListModalController'
                             resolve:
                                userListCSV: () -> userListCSV
                                userlist: () -> userlist
                          ).result.then (result) ->
                             #console.log (result)
                             $http.post("/api/lmn/sophomorixUsers/import-list", {action: 'save', data: result, userlist: userlist}).then (resp) ->
                                #console.log (resp['data'])
                                if resp['data'][0] == 'ERROR'
                                    notify.error (resp['data'][1])
                                if resp['data'][0] == 'LOG'
                                    notify.success gettext(resp['data'][1])
                                # TODO: it would be better to reload just the content frame. Currently I dont know how to set the route to reload it
                                $window.location.reload()
                                msg.close()
                                notify.success gettext('Saved')

                msg.close()
        , null, (progress) ->
          msg.messagebox.title = "Uploading: #{Math.floor(100 * progress)}%"
        )


    $scope.close = () ->
        $uibModalInstance.close()

angular.module('lm.users').controller 'LMNUsersAddAdminController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, role) ->

    $scope.role = role
    $scope.save = (username) ->
        if not $scope.username
            notify.error gettext("You have to enter a username")
            return
        else
            notify.success gettext('Adding administrator...')
            $http.post('/api/lm/users/change-'+role, {action: 'create' ,users: username}).then (resp) ->
                # console.log (resp.data)
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                $route.reload()
            $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()
