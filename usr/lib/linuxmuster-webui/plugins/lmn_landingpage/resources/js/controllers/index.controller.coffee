angular.module('lmn.landingpage').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/landingpage',
        controller: 'LMNLandingController'
        templateUrl: '/lmn_landingpage:resources/partial/index.html'

angular.module('lmn.landingpage').controller 'LMNLandingController', ($scope, $http, $uibModal, $location, gettext, notify, pageTitle, messagebox) ->
    pageTitle.set(gettext('Home'))

    $scope.getQuota = $http.post('/api/lmn/quota/').then (resp) ->
        console.log resp.data
        $scope.user = resp.data
        $scope.quotas = []

        for share, values of $scope.user['QUOTA_USAGE_BY_SHARE']
            # default-school and linuxmuster-global both needed ?
            # cloudquota and mailquota not in QUOTA_USAGE_BY_SHARE ?
            used = values['USED_MiB']
            total = values['HARD_LIMIT_MiB']
            if (typeof total == 'string')
                $scope.quotas.push({'share':share, 'total':total, 'used':used, 'usage':0})
            else
                $scope.quotas.push({'share':share, 'total':total + " MiB", 'used':used, 'usage':Math.floor((100 * used) / total)})

            $scope.groups = []
            for dn in $scope.user['memberOf']
                cn       = dn.split(',')[0].split('=')[1]
                category = dn.split(',')[1].split('=')[1]
                if (category != "Management")
                    # User don't need to see management groups
                    $scope.groups.push({'cn':cn, 'category':category})

    $scope.changePassword = () ->
        $location.path('/view/lmn/change-password');
