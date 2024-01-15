angular.module('lmn.users').controller 'LMNUsersShowPasswordController', ($scope, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, username) ->
    $scope.username = username
    user = $scope.username.replace("-exam", '')
    $scope.passwordStatus = ''

    $http.get('/api/lmn/users/passwords/' + user).then (resp) ->
        $scope.password = resp.data

    if $scope.username == user
        # Not an exam user, sophomorix can check the first password.
        $http.get("/api/lmn/users/#{user}/first-password-set").then (response) ->
            if response.data == true
                $scope.passwordStatus = gettext('Still Set')
                $scope.passwordStatusColor = 'green'
            else
                $scope.passwordStatus = gettext('Changed from user')
                $scope.passwordStatusColor = 'red'

    $scope.close = () ->
        $uibModalInstance.close()

angular.module('lmn.users').controller 'LMNUsersCustomPasswordController', ($scope, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, users, pwtype, validation) ->
    $scope.users = users
    # Single user
    if not Array.isArray(users)
        $scope.users = [users]
    $scope.pwtype = if (pwtype == 'current') then pwtype else 'first'
    $scope.userpw = ""

    $scope.save = () ->
        if not $scope.userpw
            notify.error(gettext("You have to enter a password"))
            return

        test = validation.isValidPassword($scope.userpw)
        if test != true
           notify.error gettext(test)
           return
        else
            usernames = $scope.users.flatMap((x) => x.sAMAccountName).join(',').trim()
            $http.post("/api/lmn/users/passwords/set-#{$scope.pwtype}", {users: usernames, password: $scope.userpw}).then (resp) ->
                notify.success(gettext('New password set'))
        $scope.close()

    $scope.close = () ->
        $uibModalInstance.close()

angular.module('lmn.users').controller 'LMNUserDetailsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, id, role, identity, customFields) ->

    #notify.error gettext("You have to enter a username")
    $scope.id = id
    $scope.showGroupDetails = true
    $scope.showQuotaDetails = true
    $scope.nevertext = gettext('Never')
    $scope.custom_column = false
    if role == 'schooladmins'
        custom_fields_role = 'schooladministrators'
    else if role == 'globaladmins'
        custom_fields_role = 'globaladministrators'
    else
        custom_fields_role = role

    identity.promise.then () ->
        if identity.profile.isAdmin || identity.user == 'root'
            customFields.load_config(custom_fields_role).then (resp) ->
                $scope.custom = resp.custom
                $scope.customMulti = resp.customMulti
                $scope.proxyAddresses = resp.proxyAddresses

                # Is there a custom field to show ?
                if $scope.proxyAddresses.show
                    $scope.custom_column = true

                if not $scope.custom_column
                    for custom, values of $scope.custom
                        if values.show
                            $scope.custom_column = true
                            break

                if not $scope.custom_column
                    for custom, values of $scope.customMulti
                        if values.show
                            $scope.custom_column = true
                            break

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

    $http.get("/api/lmn/sophomorixUsers/#{role}/#{id}").then (resp) ->
        $scope.userDetails = resp.data[0]
        $scope.groups = []
        for dn in $scope.userDetails['memberOf']
            cn       = dn.split(',')[0].split('=')[1]
            category = dn.split(',')[1].split('=')[1]
            $scope.groups.push({'cn':cn, 'category':category})

    $http.get("/api/lmn/quota/user/#{id}").then (resp) ->
        $scope.quotas = []

        for share, values of resp.data['QUOTA_USAGE_BY_SHARE']
        # default-school and linuxmuster-global both needed ?
        # cloudquota and mailquota not in QUOTA_USAGE_BY_SHARE ?
            used = values['USED_MiB']
            total = values['HARD_LIMIT_MiB']
            if (typeof total == 'string')
                if (total == 'NO LIMIT')
                    total = gettext('NO LIMIT')
                $scope.quotas.push({'share':share, 'total':gettext(total), 'used':used, 'usage':0, 'type':"success"})
            else
                usage = Math.floor((100 * used) / total)
                if (usage < 60)
                    type = "success"
                else if (usage < 80)
                    type = "warning"
                else
                    type = "danger"
                $scope.quotas.push({'share':share, 'total':total + " MiB", 'used':used, 'usage':usage, 'type':type})

    $scope.editCustom = (index) ->
        value = $scope.userDetails['sophomorixCustom' + index]
        customFields.editCustom($scope.id, value, index).then (resp) ->
            $scope.userDetails['sophomorixCustom' + index] = resp

    $scope.removeCustomMulti = (index, value) ->
        customFields.removeCustomMulti($scope.id, value, index).then () ->
            position = $scope.userDetails['sophomorixCustomMulti' + index].indexOf(value)
            $scope.userDetails['sophomorixCustomMulti' + index].splice(position, 1)

    $scope.addCustomMulti = (index) ->
        customFields.addCustomMulti($scope.id, index).then (resp) ->
            if resp
                $scope.userDetails['sophomorixCustomMulti' + index].push(resp)

    $scope.removeProxyAddresses = (value) ->
        customFields.removeProxyAddresses($scope.id, value).then () ->
            position = $scope.userDetails['proxyAddresses'].indexOf(value)
            $scope.userDetails['proxyAddresses'].splice(position, 1)

    $scope.addProxyAddresses = () ->
        customFields.addProxyAddresses($scope.id).then (resp) ->
            if resp
                $scope.userDetails['proxyAddresses'].push(resp)

    $scope.close = () ->
        $uibModalInstance.dismiss()



angular.module('lmn.users').controller 'LMUsersSortListModalController', ($scope, $window, $http, $uibModalInstance, messagebox, notify, $uibModal, gettext, filesystem, userlist, userListCSV) ->


    $scope.userListCSV = userListCSV
    $scope.userlist = userlist

    $scope.rebuildCSV = () ->
        # add empty 'not used' fields if CSV contains more columns than fields
        while $scope['userListCSV'].length > $scope['coloumnTitles'].length
            $scope['coloumnTitles'].push({name: gettext('not used')})

        i = 0
        for element in $scope.userListCSV
            element.coloumn = $scope.coloumnTitles[i]['id']
            i = i + 1
        #console.log ($scope['userListCSV'])


    $scope.togglecustomField = (field) ->
        # get index of field in columnTitles (-1 if not present)
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

angular.module('lmn.users').controller 'LMUsersUploadModalController', ($scope, $window, $http, $uibModalInstance, messagebox, notify, $uibModal, gettext, filesystem, role, parent) ->
    $scope.path = "/tmp/"
    $scope.parent = parent
    $scope.role = role
    $scope.csv_name = "#{role}.csv"

    $scope.upload = ($flow, check=true) ->
        $uibModalInstance.close()
        msg = messagebox.show({progress: true})
        filesystem.startFlowUpload($flow, $scope.path).then(() ->
            notify.success(gettext('Uploaded'))
            filename = $flow["files"][0]["name"]
            if check
                $scope.checkColumns(filename)
            else
                $scope.saveCSV(filename)
            msg.close()
        , null, (progress) ->
            msg.messagebox.title = "Uploading: #{Math.floor(100 * progress)}%"
        )

    $scope.checkColumns = (filename) ->
        $http.post('/api/lmn/users/lists/import', {action: 'get', path: $scope.path+filename, userlist: $scope.csv_name}).then (resp) ->
            userListCSV = resp.data
            $uibModal.open(
                templateUrl: '/lmn_users:resources/partial/sortList.modal.html'
                controller: 'LMUsersSortListModalController'
                resolve:
                    userListCSV: () -> userListCSV
                    userlist: () -> $scope.csv_name
            ).result.then (result) ->
                 $http.post("/api/lmn/users/lists/import", {action: 'save', data: result, userlist: $scope.csv_name}).then (resp) ->
                    #console.log (resp['data'])
                    if resp['data'][0] == 'ERROR'
                        notify.error (resp['data'][1])
                    if resp['data'][0] == 'LOG'
                        $scope.parent["get#{$scope.role}"](force:true)
                        notify.success gettext(resp['data'][1])
                        notify.success gettext('Saved')

    $scope.saveCSV = (filename) ->
        $http.post('/api/lmn/users/lists/csv', {tmp_path: $scope.path + filename, userlist: $scope.csv_name}).then (resp) ->
            if resp['data'][0] == 'ERROR'
                notify.error (resp['data'][1])
            if resp['data'][0] == 'LOG'
                $scope.parent["get#{$scope.role}"](force:true)
                notify.success gettext(resp['data'][1])
                notify.success gettext('Saved')

    $scope.close = () ->
        $uibModalInstance.close()

angular.module('lmn.users').controller 'LMNUsersAddAdminController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, role) ->

    $scope.role = role
    $scope.save = (username) ->
        if not $scope.username
            notify.error gettext("You have to enter a username")
            return
        else
            notify.success gettext('Adding administrator...')
            $http.post("/api/lmn/sophomorixUsers/#{role}s", {users: username}).then (resp) ->
                # console.log (resp.data)
                if resp['data'][0] == 'ERROR'
                    notify.error (resp['data'][1])
                if resp['data'][0] == 'LOG'
                    notify.success gettext(resp['data'][1])
                $route.reload()
            $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()
