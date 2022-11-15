angular.module('lmn.users').controller 'LMUsersCheckResultsModalController', ($scope, $uibModalInstance, $uibModal, data, gettext) ->
    $scope.data = data
    $scope._ = {
        doAdd: data['SUMMARY'][1]['ADD']['RESULT'] > 0
        doMove: data['SUMMARY'][2]['UPDATE']['RESULT'] > 0
        doKill: data['SUMMARY'][3]['KILL']['RESULT'] > 0
    }

    $scope.tab_selected = "all"
    $scope.tab_selected_text = {
        "all" : gettext('Apply'),
        "add" : gettext('Add user(s)'),
        "move" : gettext('Move user(s)'),
        "kill" : gettext('Kill user(s)'),
        "error" : gettext('Errors'),
    }
    $scope.select = (tab) ->
        $scope.tab_selected = tab

    ## Use same string status for, e.g., Removable and Killable ?
    $scope.user_status = {
        'U' : 'Usable (U)',
        'A' : 'Activated (A)',
        'E' : 'Enabled (E)',
        'S' : 'Self-activated (S)',
        'P' : 'Permanent (P)',
        'T' : 'Tolerated (T)',
        'L' : 'Locked (L)',
        'D' : 'Deactivated (D)',
        'F' : 'Frozen (F)',
        'R' : 'Removable (R)',
        'K' : 'Killable (K)',
        'X' : 'Exam (X)',
        'M' : 'Managed (M)',
    }

    $scope.status_filter = (status) ->
        if $scope.user_status[status] == undefined
            return status
        else
            return $scope.user_status[status]

    $scope.apply = (mode) ->
        if mode == "add"
            $scope._ = {doAdd: true, doMove: false, doKill: false}
        if mode == "move"
            $scope._ = {doAdd: false, doMove: true, doKill: false}
        if mode == "kill"
            $scope._ = {doAdd: false, doMove: false, doKill: true}
        $uibModalInstance.close()
        msg = $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/apply.modal.html'
            controller: 'LMUsersApplyModalController'
            backdrop: 'static'
            size: 'lg'
            resolve:
                params: () -> $scope._
        )

        $uibModalInstance.close()

    $scope.cancel = () ->
        $uibModalInstance.dismiss()


angular.module('lmn.users').controller 'LMUsersApplyModalController', ($scope, $uibModalInstance, $http, $route, gettext, notify, params) ->
    $scope.options = {
       autoscroll: true
    }

    $scope.close = () ->
        $uibModalInstance.close()

    $scope.isWorking = true
    $http.post('/api/lmn/users/lists/apply', params).then (resp) ->
        $scope.isWorking = false
        notify.success gettext('Changes applied')
        $route.reload()

    .catch (resp) ->
        $scope.isWorking = false
        notify.error gettext('Failed'), resp.data.message



angular.module('lmn.users').controller 'LMUsersCheckModalController', ($scope, $http, notify, $uibModalInstance, $uibModal, gettext) ->
    $scope.isWorking = true

    $http.get('/api/lmn/users/lists/check').then (resp) ->
        if not resp.data
            notify.error gettext('Unknown error!'), gettext('Please run sophomorix-check manually to identity the reason.')
            $uibModalInstance.close()
            return

        if resp.data["OUTPUT"][0]["TYPE"] == "ERROR"
            notify.error(resp.data["OUTPUT"][0]["MESSAGE_EN"])
            $scope.error = true
            $scope.isWorking = false
            $uibModalInstance.close()
            return

        if resp.data["CHECK_RESULT"]["ERRORLIST"].length > 0
            notify.error(gettext('Check failed'))
            $scope.isWorking = false
            $scope.error = true
            $scope.errorList = resp.data["CHECK_RESULT"]['ERROR']
        else
            $scope.showCheckResults(resp.data)
            $uibModalInstance.close()
    .catch (resp) ->
        $scope.isWorking = false
        $scope.error = true
        notify.error(gettext('Check failed'), resp.data.message)

    $scope.showCheckResults = (data) ->
        $uibModal.open(
            templateUrl: '/lmn_users:resources/partial/result.modal.html'
            controller: 'LMUsersCheckResultsModalController'
            resolve:
                data: () -> data
        )

    $scope.close = () ->
        $uibModalInstance.close()
