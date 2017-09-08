angular.module('lm.setup_wizard', [
    'core',
    'ajenti.network',
])

angular.module('lm.setup_wizard').run((config, $location, identity) => {
    identity.promise.then(() => config.promise).then(() => {
        if (identity.user && (!config.data.linuxmuster || !config.data.linuxmuster.initialized)) {
            return $location.path('/view/lm/init/welcome')
        }
    })
})
