angular.module 'lmn.auth', [
    'core',
]

angular.module('lmn.auth').run (customization, $http, identity, gettextCatalog, config) ->
    lang = config.data.language || 'en'
    $http.get("/resources/all.locale.js?lang=#{lang}").then (rq) ->
            gettextCatalog.setStrings(lang, rq.data)
            expr = rq.data['Change password']

            customization.plugins.core.extraProfileMenuItems = [
                {
                    url: '/view/lmn/change-password',
                    name: expr,
                    icon: 'key'
                }
            ]
