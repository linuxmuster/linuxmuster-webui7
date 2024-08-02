angular.module('lmn.common').config(($routeProvider) => {
    $routeProvider.when('/view/lmn/change-school', {
        templateUrl: '/lmn_common:resources/partial/schoolswitcher.html',
        controller: 'LMNSchoolSwitcherController',
    });
})  

angular.module('lmn.common').controller('LMNSchoolSwitcherController', function ($scope, $http, pageTitle, gettext, notify, $uibModal, $window) {
    pageTitle.set(gettext('Schoolswitcher'));

    $scope.load = () => {
        $http.get('/api/lmn/activeschool').then((resp) => {
            $scope.activeschool = resp.data;
        });
    
        $http.get('/api/lmn/list-schools').then((resp) => {
            $scope.schools = resp.data;
        });
    }

    $scope.switchSchool = (school) => {
        $http.post('/api/lmn/change-school', { school: school }).then((resp) => {
            if(resp.data) {
                notify.success("School changed successfully");
            }
            else {
                notify.error("Failed to change school!");
            }
            $scope.load();
        });
    }

    $scope.load();
})
