angular.module('lmn.users').service('userPassword', function($http, $uibModal, messagebox, notify, gettext) {

    this.showFirstPassword = (username) => {
        return $uibModal.open({
            templateUrl: '/lmn_users:resources/partial/showPassword.modal.html',
            controller: 'LMNUsersShowPasswordController',
            keyboard: false,
            backdrop: false,
            resolve:{
                username: () => username
            }
        }).result;
    };

    this.resetFirstPassword = (userlist) => {
        $http.post('/api/lmn/users/passwords/reset-first', {users: userlist}).then((resp) => {
            notify.success(gettext('Initial password set'));
        });
    };

    this.setRandomFirstPassword = (userlist) => {
        $http.post('/api/lmn/users/passwords/set-random', {users: userlist}).then((resp) => {
            notify.success(gettext('Random password set'));
        });
    };

    this.setCustomPassword = (userlist, pwtype) => {
        // type may be 'first' or 'current'
        $uibModal.open({
            templateUrl: '/lmn_users:resources/partial/customPassword.modal.html',
            controller: 'LMNUsersCustomPasswordController',
            size: 'mg',
            resolve: {
                users: () => userlist,
                pwtype: () => pwtype,
            }
        });
    };

    this.batchPasswords = (userlist, cmd) => {
        usernames = userlist.flatMap((x) => x.selected ? x.sAMAccountName : [] ).join(',').trim();
        users = userlist.filter((x) => x.selected);
        if (cmd == 'reset-first') {
            this.resetFirstPassword(usernames);
        }
        else if (cmd == 'random-first') {
            this.setRandomFirstPassword(usernames);
        }
        else if (cmd == 'custom-first') {
            this.setCustomPassword(users, 'first');
        };
    };

    this.showBindPW = (user) => {
        messagebox.show({
            title: gettext('Show bind user password'),
            text: gettext("Do you really want to see this password ? It could be a security issue!"),
            positive: 'Show',
            negative: 'Cancel'}).then(() => {
                $http.post('/api/lm/users/showBindPW', {user: user.sAMAccountName}).then((resp) => {
                    messagebox.show({title: gettext('Show bind user password'), text: resp.data, positive: 'OK'});
                });
            });
    };

    return this;
});