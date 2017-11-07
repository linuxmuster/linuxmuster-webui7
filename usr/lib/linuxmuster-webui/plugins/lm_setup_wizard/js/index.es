angular.module('lm.setup_wizard', [
    'core',
    'ajenti.network',
])

angular.module('lm.setup_wizard').run(($http, $location, identity) => {
    identity.promise.then(() => {
      if (identity.user) {
        $http.get('/api/lm/setup-wizard/is-configured').then(response => {
          if (!response.data) {
            $location.path('/view/lm/init/welcome')
          }
        })
      }
    })
})
