angular.module('lmn.setup_wizard', [
    'core',
])

angular.module('lmn.setup_wizard').run(($http, $location, identity) => {
    identity.promise.then(() => {
      if (identity.user) {
        $http.get('/api/lmn/setup-wizard/is-configured').then(response => {
          if (!response.data) {
            $location.path('/view/lmn/init/welcome')
          }
        })
      }
    })
})
