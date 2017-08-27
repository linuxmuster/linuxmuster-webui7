angular.module('lm.setup_wizard', [
    'core',
])

angular.module('lm.setup_wizard').run((config, $location) => {
    config.promise.then(() => {
        if (!config.data.linuxmuster || !config.data.linuxmuster.initialized) {
            return $location.path('/view/lm/init/welcome')
        }
    })
})
