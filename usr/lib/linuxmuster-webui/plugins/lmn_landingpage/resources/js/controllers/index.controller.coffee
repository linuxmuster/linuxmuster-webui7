angular.module('lmn.landingpage').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/landingpage',
        controller: 'LMNLandingController'
        templateUrl: '/lmn_landingpage:resources/partial/index.html'

angular.module('lmn.landingpage').controller 'LMNLandingController', ($scope, $http, $uibModal, $location, $route, gettext, notify, pageTitle) ->
    pageTitle.set(gettext('Home'))

    $scope.getData = (user) ->
        $http.get("/api/lmn/custom_fields/#{user}").then (resp) ->
            $scope.custom_fields = resp.data

        $http.get("/api/lmn/quota/#{user}").then (resp) ->
            $scope.quotas = []
            $scope.user['sophomorixCloudQuotaCalculated'] = resp.data['sophomorixCloudQuotaCalculated']
            $scope.user['sophomorixMailQuotaCalculated'] = resp.data['sophomorixMailQuotaCalculated']

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

    $scope.list_attr_enabled = ['proxyAddresses']
    for n in [1,2,3,4,5]
        $scope.list_attr_enabled.push('sophomorixCustomMulti' + n)

    $scope.isListAttr = (attr_name) ->
        return $scope.list_attr_enabled.includes(attr_name)

    $scope.changePassword = () ->
        $location.path('/view/lmn/change-password');

    $scope.changeCustomFields = () ->
       $uibModal.open(
          templateUrl: '/lmn_landingpage:resources/partial/customFields.modal.html'
          controller: 'LMNUserCustomFieldsController'
          size: 'md'
          resolve:
             custom_fields: () -> $scope.custom_fields
             user: () -> $scope.user
             ).closed.then () ->
                $route.reload()

    $scope.$watch 'identity.user', ->
        if $scope.identity.user is undefined
           return
        if $scope.identity.user is null
           return
        if $scope.identity.user is 'root'
           return

        $scope.user = $scope.identity.profile
        $scope.getData($scope.identity.user)
        $scope.groups = []

        for dn in $scope.user['memberOf']
            cn       = dn.split(',')[0].split('=')[1]
            category = dn.split(',')[1].split('=')[1]
            if (category != "Management")
            # User don't need to see management groups
            # User only see explicit lmn groups, no custom groups

            # Determine classes by group dn
                if (category == cn)
                    $scope.groups.push({'cn':cn, 'category':gettext('Class')})
                if (category == "Teachers")
                    $scope.groups.push({'cn':cn, 'category':gettext('Teachers')})
                if (category == "printer-groups")
                    $scope.groups.push({'cn':cn, 'category':gettext('Printers')})
                if (category == "Projects")
                    $scope.groups.push({'cn':cn, 'category':gettext('Project')})
        return

angular.module('lmn.users').controller 'LMNUserCustomFieldsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, user, custom_fields) ->

    $scope.custom_fields = custom_fields
    $scope.user = user
    $scope.id = user.sAMAccountName

    $scope.list_attr_enabled = ['proxyAddresses']
    for n in [1,2,3,4,5]
        $scope.list_attr_enabled.push('sophomorixCustomMulti' + n)

    $scope.isListAttr = (attr_name) ->
        return $scope.list_attr_enabled.includes(attr_name)

    $scope.editCustom = (custom) ->
        value = custom.value
        n = custom.attr.slice(-1)
        messagebox.prompt(gettext('New value'), value).then (msg) ->
            $http.post("/api/lm/custom", {index: n, value: msg.value, user: $scope.id}).then () ->
                if msg.value
                    custom.value = msg.value
                else
                    custom.value = 'null'
                notify.success(gettext("Value updated !"))
            , () ->
                notify.error(gettext("Error, please verify the user and/or your values."))

    $scope.removeCustomMulti = (custom, value) ->
        n = custom.attr.slice(-1)
        messagebox.show(
            title: gettext('Remove custom field value'),
            text: gettext('Do you really want to remove ') + value + ' ?',
            positive: gettext('OK'),
            negative: gettext('Cancel')
        ).then (msg) ->
            $http.post("/api/lm/custommulti/remove", {index: n, value: value, user: $scope.id}).then () ->
                position = custom.value.indexOf(value)
                custom.value.splice(position, 1)
                notify.success(gettext("Value removed !"))
            , () ->
                notify.error(gettext("Error, please verify the user and/or your values."))

    $scope.addCustomMulti = (custom) ->
        n = custom.attr.slice(-1)
        messagebox.prompt(gettext('New value')).then (msg) ->
            $http.post("/api/lm/custommulti/add", {index: n, value: msg.value, user: $scope.id}).then () ->
                if msg.value
                    custom.value.push(msg.value)
                    notify.success(gettext("Value added !"))
                    console.log(custom)
            , () ->
                notify.error(gettext("Error, please verify the user and/or your values."))

    $scope.removeProxyAddresses = (custom, value) ->
        messagebox.show(
            title: gettext('Remove proxy address'),
            text: gettext('Do you really want to remove ') + value + ' ?',
            positive: gettext('OK'),
            negative: gettext('Cancel')
        ).then (msg) ->
            $http.post("/api/lm/changeProxyAddresses", {action: 'remove', address: value, user: $scope.id}).then () ->
                position = custom.value.indexOf(value)
                custom.value.splice(position, 1)
                notify.success(gettext("Value removed !"))
            , () ->
                notify.error(gettext("Error, please verify the user and/or your values."))

    $scope.addProxyAddresses = (custom) ->
        n = custom.attr.slice(-1)
        messagebox.prompt(gettext('New address')).then (msg) ->
            $http.post("/api/lm/changeProxyAddresses", {action: 'add', address: msg.value, user: $scope.id}).then () ->
                if msg.value
                    custom.value.push(msg.value)
                notify.success(gettext("Address added !"))
            , () ->
                notify.error(gettext("Error, please verify the user and/or your values."))

    $scope.close = () ->
        $uibModalInstance.dismiss()