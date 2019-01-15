// the module should depend on 'core' to use the stock services & components
angular.module('example.lmn_landing', [
    'core',
]);

angular.module('example.lmn_landing').config(($routeProvider) => {
    $routeProvider.when('/view/lmn_landing', {
        template: '<lmn_landing></lmn_landing>',
    });
});

angular.module('example.lmn_landing').component('lmn_landing', {
    templateUrl: '/lmn_landing:resources/index.html',
    controller: function (notify, pageTitle) {
        let ctrl = this;

        pageTitle.set('Lmn_landing');

        ctrl.counter = 0;

        ctrl.click = () => {
            ctrl.counter += 1;
            notify.info('+1');
        };

        return this;
    }
});
