'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('lmn.samba_dns', ['core']);


'use strict';

angular.module('lmn.samba_dns').config(function ($routeProvider) {
    $routeProvider.when('/view/lm/samba_dns', {
        templateUrl: '/lmn_samba_dns:resources/partial/index.html',
        controller: 'SambaDnsIndexController'
    });
});


'use strict';

angular.module('lmn.samba_dns').controller('SambaDnsIndexController', function ($scope, $http, pageTitle, gettext, notify, messagebox) {
    pageTitle.set(gettext('Samba_dns'));

    $scope.trans = {
        'modify': gettext('Modify this entry'),
        'delete': gettext('Delete this entry')
    };

    $scope.showUpdate = false;
    $scope.showNew = false;
    $scope.types = ['AAAA', 'A', 'PTR', 'CNAME', 'NS', 'MX', 'TXT'];

    $http.get('/api/dns/get').then(function (resp) {
        $scope.entries = resp.data[0];
        $scope.zone = resp.data[1];
    });

    $scope.delete = function (sub) {
        messagebox.show({
            text: "Do you really want to delete this entry?",
            positive: 'Delete',
            negative: 'Cancel'
        }).then(function () {
            $http.post('/api/dns/delete', { sub: sub.host, type: sub.type, value: sub.value }).then(function (resp) {
                notify.success(gettext('Entry deleted !'));
                position = $scope.entries.sub.indexOf(sub);
                $scope.entries.sub.splice(position, 1);
            });
        });
    };

    $scope.add = function (sub) {
        $scope.showNew = true;
        $scope.new = { 'host': '', 'type': 'A', 'value': '' };
    };

    $scope.show_update = function (sub) {
        $scope.old_sub = angular.copy(sub);
        $scope.sub = sub;
        $scope.showUpdate = true;
    };

    $scope.update = function () {
        $scope.showUpdate = false;
        $http.post('/api/dns/update', { old: $scope.old_sub, new: $scope.sub }).then(function (resp) {
            notify.success(gettext('Entry updated !'));
        });
    };

    $scope.close = function () {
        $scope.showUpdate = false;
        $scope.showNew = false;
    };

    $scope.save = function () {
        $scope.showNew = false;
        $http.post('/api/dns/add', { sub: $scope.new }).then(function (resp) {
            notify.success(gettext('Entry saved !'));
            $scope.entries.sub.push($scope.new);
        });
    };
});


