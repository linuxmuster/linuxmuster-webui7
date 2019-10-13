angular.module 'lm.auth', [
    'core',
]

angular.module('lm.auth').run (customization, gettext, identity) ->
    customization.plugins.core.extraProfileMenuItems = [
        {
            url: '/view/lmn/change-password',
            name: gettext('Change password'),
            icon: 'key'
        }
    ]
