angular.module('lmn.common').service('customFields', function($http) {

    this.customDisplayOptions = [
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
        return $http.get(`/api/lm/read_custom_config/${role}`).then(response => {
            // Filter title per display
            config = {
                'customDisplay': response.data.customDisplay,
                'customTitle': ['', '', '', ''],
            };
            for (idx of [1,2,3]) {
                if (config['customDisplay'][idx] == 'proxyAddresses') {
                    config['customTitle'][idx] = response.data.proxyAddresses.title;
                } else {
                    index = config['customDisplay'][idx].slice(-1);
                    if (this.isListAttr(config['customDisplay'][idx])) {
                        config['customTitle'][idx] = response.data.customMulti[index].title || '';
                    } else {
                        config['customTitle'][idx] = response.data.custom[index].title || '';
                    }
                }
            }
            return config;
        });
    }

    this.load_config = (role='') =>
        $http.get(`/api/lm/read_custom_config/${role}`).then(response => response.data)

    this.load_user_fields = (user) =>
        $http.get(`/api/lmn/custom_fields/${user}`).then(response => response.data)

    this.save = (config) =>
        $http.post("/api/lm/save_custom_config", {'config':config})

    return this;
});