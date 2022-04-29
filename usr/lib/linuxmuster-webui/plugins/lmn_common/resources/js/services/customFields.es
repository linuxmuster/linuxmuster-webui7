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

    this.load_config = (role='') =>
        $http.get(`/api/lm/read_custom_config/${role}`).then(response => response.data)

    this.save = (config) =>
        $http.post("/api/lm/save_custom_config", {'config':config})

    return this;
});