angular.module 'lm.auth', [
    'core',
]

angular.module('lm.auth').run (customization, identity) ->
    customization.plugins.core.extraProfileMenuItems = [
        {
            url: '/view/lm/change-password',
            name: 'Change password',
            icon: 'key'
        }
    ]
