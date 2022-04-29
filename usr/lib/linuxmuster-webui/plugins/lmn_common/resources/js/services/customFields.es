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

    this.load_config = (role='') => {
        return $http.get(`/api/lm/read_custom_config/${role}`).then(response => {
            if (role) {
                // Filter title per display
                customDisplay = response.data.customDisplay;
                customTitle = ['', '', '', ''];
                for (idx of [1,2,3]) {
                    if (customDisplay[idx] == 'proxyAddresses') {
                        customTitle[idx] = response.data.proxyAddresses.title;
                    } else {
                        index = customDisplay[idx].slice(-1);
                        if (this.isListAttr(customDisplay[idx])) {
                            customTitle[idx] = response.data.customMulti[index].title || '';
                        } else {
                            customTitle[idx] = response.data.custom[index].title || '';
                        }
                    }
                }
                return [customDisplay, customTitle];
            }
            else {
                return response.data;
            }
        });
    }


    this.save = (config) =>
        $http.post("/api/lm/save_custom_config", {'config':config})

    return this;
});