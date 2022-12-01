angular.module('lmn.permissions').controller 'PermissionListIndexController', ($scope, $http, $interval, $timeout, notify, pageTitle, messagebox, gettext, config) ->
    pageTitle.set(gettext('List all permissions'))

    $scope.query = {
        'plugin': '',
        'sidebar': ''
    }
    $scope.columns = ['globaladministrator', 'schooladministrator', 'teacher', 'student', 'default']


    $scope.roles = ['globaladministrator', 'schooladministrator', 'teacher', 'student']
    $http.get('/api/lmn/permissions').then (resp) ->

        $scope.pluginObj = resp.data[0]
        # To iterate in alphabetical order
        $scope.pluginList = Object.keys($scope.pluginObj)
        $scope.pluginList.sort()

        $scope.apiPermissions = resp.data[1]
        $scope.sidebarPermissions = resp.data[2]
        # To iterate in alphabetical order
        $scope.sidebarPermissionsList = Object.keys($scope.sidebarPermissions)
        $scope.sidebarPermissionsOrphans = []
        for url in $scope.sidebarPermissionsList
            if $scope.sidebarPermissions[url].plugin == 'NOT IMPLEMENTED'
                $scope.sidebarPermissionsOrphans.push(url)
        $scope.apiPermissionsOrphans = []
        for url, details of $scope.apiPermissions
            if details.name == 'NO DESCRIPTION'
                $scope.apiPermissionsOrphans.push(url)
        $scope.sidebarPermissionsList.sort()

    $scope.get_provider = (url) ->
        if url.includes('/lm')
            return "Linuxmuster.net"
        if url.includes('/ni')
            return "Netzint"
        return "Ajenti"

    $scope.providerLogo = (provider) ->
        if provider == "Linuxmuster.net"
            return "logo-x.png"
        if provider == "Netzint"
            return "logo-ni.png"
        if provider == "Ajenti"
            return "logo-ajenti.png"

    $scope.methodLabelClass = (method) ->
        if method == "get"
            return "success"
        if method == "post"
            return "primary"
        if method == "put"
            return "info"
        if method == "delete" || method == "patch"
            return "danger"
        return "default"

    $scope.iconify = (bool) ->
        if typeof(bool) == "undefined"
            return 'question'
        if bool == "true" or bool == true
            return 'check'
        return 'times'

    $scope.colorize = (bool) ->
        if typeof(bool) == "undefined"
            return ''
        if bool == "true" or bool == true
            return 'color:green'
        return 'color:red'

    $scope.count_rows = (plugin) ->
        return document.getElementById('table_'+plugin).rows.length > 1

    $scope.switch = (obj, role) ->
        # Set the filter to role
        # obj may be plugin or sidebar
        if $scope.query[obj] == role
            $scope.query[obj] = ''
        else
            $scope.query[obj] = role

    $scope.changeApi = (details, role) ->
        state = $scope.apiPermissions[details.permission_id][role]
        # Cycle undefined -> false -> true
        states = [undefined, "false", "true"]
        $scope.apiPermissions[details.permission_id][role] = states[(states.indexOf(state)+1) % 3]

    $scope.changeSidebar = (url, role) ->
        state = $scope.sidebarPermissions[url][role]
        # Cycle undefined -> false -> true
        states = [undefined, "false", "true"]
        $scope.sidebarPermissions[url][role] = states[(states.indexOf(state)+1) % 3]

    $scope.filter_sidebar = (url) ->
        details = $scope.sidebarPermissions[url]
        if $scope.roles.indexOf($scope.query.sidebar) != -1
            return details[$scope.query.sidebar] == "true"
        else
            return url.includes($scope.query.sidebar)
        return true

    $scope.filter_plugin = (plugin) ->
        if $scope.roles.indexOf($scope.query.plugin) != -1
            return true
        return plugin.includes($scope.query.plugin)

    $scope.filter_api = (details) ->
        if $scope.roles.indexOf($scope.query.plugin) != -1
            if details.permission_id
                return $scope.apiPermissions[details.permission_id][$scope.query.plugin] == "true"
            else
                return false
        return true

    $scope.export = () ->
        $http.post('/api/lmn/permissions/export', {
            'api': $scope.apiPermissions,
            'sidebar': $scope.sidebarPermissions,
            'pluginDict': $scope.pluginObj,
        })