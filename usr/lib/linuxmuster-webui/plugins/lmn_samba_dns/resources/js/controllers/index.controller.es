angular.module('lmn.samba_dns').controller('SambaDnsIndexController', function($scope, $http, pageTitle, gettext, notify, messagebox) {
    pageTitle.set(gettext('Samba_dns'));

    $scope.trans = {
        'modify' : gettext('Modify this entry'),
        'delete' : gettext('Delete this entry')
    }

    $scope.showUpdate = false;
    $scope.showNew = false;
    $scope.types = ['AAAA', 'A', 'PTR', 'CNAME', 'NS', 'MX', 'TXT']

    $http.get('/api/lmn/dns').then( (resp) => {
	    $scope.entries = resp.data[0];
        $scope.zone = resp.data[1];
    });

    $scope.delete = (sub) => {
        messagebox.show({
            text: "Do you really want to delete this entry?",
            positive: 'Delete',
            negative: 'Cancel'
        }).then( () => {
            if (sub.type == 'MX')
                value = `${sub.value}\\ ${sub.priority}`;
            else
                value = sub.value;
            $http.patch('/api/lmn/dns', {sub: sub.host, type: sub.type, value: value}).then((resp) => {
                notify.success(gettext('Entry deleted !'));
                position = $scope.entries.sub.indexOf(sub);
                $scope.entries.sub.splice(position, 1);
            });
        });
    }

    $scope.add = (sub) => {
        $scope.showNew = true;
        $scope.new = {'host':'', 'type':'A', 'value':''};
    }

    $scope.show_update = (sub) => {
        $scope.old_sub = angular.copy(sub);
        $scope.sub = sub;
        $scope.showUpdate = true;
    }

    $scope.update = () => {
        $scope.showUpdate = false;
        $http.post('/api/lmn/dns', {old: $scope.old_sub, new: $scope.sub}).then((resp) => {
            notify.success(gettext('Entry updated !'));
        });
    }

    $scope.close = () => {
        $scope.showUpdate = false;
        $scope.showNew = false;
    }

    $scope.save = () => {
        $scope.showNew = false;
        $http.put('/api/lmn/dns', {sub: $scope.new}).then((resp) => {
            notify.success(gettext('Entry saved !'));
            $scope.entries.sub.push($scope.new);
        });
    }

});

