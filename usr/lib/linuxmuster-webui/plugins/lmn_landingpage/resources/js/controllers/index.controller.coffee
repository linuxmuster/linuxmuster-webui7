angular.module('lmn.landingpage').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/landingpage',
        controller: 'LMNLandingController'
        templateUrl: '/lmn_landingpage:resources/partial/index.html'

angular.module('lmn.landingpage').controller 'LMNLandingController', ($scope, $http, $uibModal, $location, $route, gettext, notify, pageTitle, customFields) ->
    pageTitle.set(gettext('Home'))

    $http.get("/api/lmn/display_options").then (resp) ->
        $scope.show_webdav = resp.data['show_webdav']

    $scope.getData = (user) ->
        customFields.load_user_fields(user).then (resp) ->
            $scope.custom_fields = resp

        $http.get("/api/lmn/quota/user/#{user}").then (resp) ->
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

    $scope.isListAttr = (attr_name) ->
        return customFields.isListAttr(attr_name)

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

    $scope.showWebappQR = () ->
       $uibModal.open(
          templateUrl: '/lmn_landingpage:resources/partial/webappqr.modal.html'
          controller: 'LMNUserWebAppQRController'
          size: 'lg'
          resolve:
             user: () -> $scope.user
             )

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

angular.module('lmn.landingpage').controller 'LMNUserCustomFieldsController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, notify, messagebox, pageTitle, user, customFields, custom_fields) ->

    $scope.custom_fields = custom_fields
    $scope.user = user
    $scope.id = user.sAMAccountName

    $scope.isListAttr = (attr_name) ->
        return customFields.isListAttr(attr_name)

    $scope.editCustom = (custom) ->
        value = custom.value
        index = custom.attr.slice(-1)
        customFields.editCustom($scope.id, value, index).then (resp) ->
            custom.value = resp

    $scope.removeCustomMulti = (custom, value) ->
        index = custom.attr.slice(-1)
        customFields.removeCustomMulti($scope.id, value, index).then () ->
            position = custom.value.indexOf(value)
            custom.value.splice(position, 1)

    $scope.addCustomMulti = (custom) ->
        index = custom.attr.slice(-1)
        customFields.addCustomMulti($scope.id, index).then (resp) ->
            if resp
                custom.value.push(resp)

    $scope.removeProxyAddresses = (custom, value) ->
        customFields.removeProxyAddresses($scope.id, value).then () ->
            position = custom.value.indexOf(value)
            custom.value.splice(position, 1)

    $scope.addProxyAddresses = (custom) ->
        customFields.addProxyAddresses($scope.id).then (resp) ->
            if resp
                custom.value.push(resp)

    $scope.close = () ->
        $uibModalInstance.dismiss()

angular.module('lmn.landingpage').controller 'LMNUserWebAppQRController', ($scope, $route, $uibModal, $uibModalInstance, $http, gettext, pageTitle, user) ->

    $scope.user = user
    $http.get("/api/webdav/qrcode").then (resp) ->
        $scope.qrdata = resp.data

    $scope.close = () ->
        $uibModalInstance.dismiss()