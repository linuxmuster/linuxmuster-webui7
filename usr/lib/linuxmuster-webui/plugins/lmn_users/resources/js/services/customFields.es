angular.module('lmn.common').service('customFields', function($http, messagebox, gettext, notify) {

    this.customDisplayOptions = [
        '',
        'proxyAddresses',
        'sophomorixCustom1',
        'sophomorixCustom2',
        'sophomorixCustom3',
        'sophomorixCustom4',
        'sophomorixCustom5',
        'sophomorixCustomMulti1',
        'sophomorixCustomMulti2',
        'sophomorixCustomMulti3',
        'sophomorixCustomMulti4',
        'sophomorixCustomMulti5',
    ]

    this.customLists = [
        'proxyAddresses',
        'sophomorixCustomMulti1',
        'sophomorixCustomMulti2',
        'sophomorixCustomMulti3',
        'sophomorixCustomMulti4',
        'sophomorixCustomMulti5',
    ]

    this.isListAttr = (attr) => this.customLists.includes(attr);

    this.load_display = (role) => {
        return $http.get(`/api/lmn/config/customfields/${role}`).then(response => {
            // Filter title per display
            config = {
                'customDisplay': response.data.customDisplay,
                'customTitle': ['', '', '', ''],
            };
            for (idx of [1,2,3]) {
                if (config['customDisplay'][idx] == 'proxyAddresses') {
                    config['customTitle'][idx] = response.data.proxyAddresses.title;
                } else {
                    position = (config['customDisplay'][idx] || '').slice(-1);
                    if (position == '') {
                        config['customTitle'][idx] = '';
                    } else if (this.isListAttr(config['customDisplay'][idx])) {
                        config['customTitle'][idx] = response.data.customMulti[position].title || '';
                    } else {
                        config['customTitle'][idx] = response.data.custom[position].title || '';
                    }
                }
            }
            return config;
        });
    }

    this.load_config = (role='') =>
        $http.get(`/api/lmn/config/customfields/${role}`).then(response => response.data)

    this.load_user_fields = (user) =>
        $http.get(`/api/lmn/users/${user}/customfields`).then(response => response.data)

    this.save = (config) =>
        $http.post("/api/lmn/config/customfields", {'config':config})

    this.editCustom = (user, value, index) => {
        return messagebox.prompt(gettext('New value'), value).then((msg) => {
            return $http.post(`/api/lmn/users/${user}/custom/${index}`, {value: msg.value}).then(() => {
                notify.success(gettext("Value updated !"));
                return msg.value || 'null';
            }, () =>
                notify.error(gettext("Error, please verify the user and/or your values."))
            );
        });
    };

    this.removeCustomMulti = (user, value, index) => {
        return messagebox.show({
            title: gettext('Remove custom field value'),
            text: gettext('Do you really want to remove ') + value + ' ?',
            positive: gettext('OK'),
            negative: gettext('Cancel')
            }).then((msg) => {
                return $http.patch(`/api/lmn/users/${user}/custommulti/${index}`, {'value': value}).then(() => {
                    notify.success(gettext("Value removed !"))});
            }, () => {
                notify.error(gettext("Error, please verify the user and/or your values."));
            });
    };

    this.addCustomMulti = (user, index) => {
        return messagebox.prompt(gettext('New value')).then((msg) => {
            return $http.post(`/api/lmn/users/${user}/custommulti/${index}`, {'value': msg.value}).then(() => {
                notify.success(gettext("Value added !"));
                return msg.value;
            }, () => {
                notify.error(gettext("Error, please verify the user and/or your values."));
            });
        });
    };

    this.removeProxyAddresses = (user, value) => {
        return messagebox.show({
            title: gettext('Remove proxy address'),
            text: gettext('Do you really want to remove ') + value + ' ?',
            positive: gettext('OK'),
            negative: gettext('Cancel')
        }).then((msg) => {
            return $http.patch(`/api/lmn/users/${user}/proxyaddresses`, {address: value}).then(() => {
                notify.success(gettext("Value removed !"));
            }, () => {
                notify.error(gettext("Error, please verify the user and/or your values."));
            });
        });
    };

    this.addProxyAddresses = (user) => {
        return messagebox.prompt(gettext('New address')).then((msg) => {
            return $http.post(`/api/lmn/users/${user}/proxyaddresses`, {address: msg.value}).then(() => {
                notify.success(gettext("Address added !"));
                return msg.value;
            }, () => {
                notify.error(gettext("Error, please verify the user and/or your values."));
            });
        });
    };

    return this;
});
