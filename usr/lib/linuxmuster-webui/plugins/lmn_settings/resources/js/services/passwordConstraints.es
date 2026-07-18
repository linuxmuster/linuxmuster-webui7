angular.module('lmn.settings').service('passwordConstraints', function($http) {

    this.load = () =>
        $http.get('/api/lmn/config/passwordconstraints').then(response => response.data)

    this.save = (config) =>
        $http.post('/api/lmn/config/passwordconstraints', {'config': config})

    return this;
});
