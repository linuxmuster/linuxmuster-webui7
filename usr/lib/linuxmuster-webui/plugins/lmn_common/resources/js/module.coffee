angular.module 'lmn.common', [
    'core',
    'ajenti.ace',
    'ajenti.filesystem',
]

angular.module('lmn.common').run (customization) ->
    customization.plugins.core.startupURL = '/view/lmn/landingpage'
    customization.plugins.core.loginredir = '/'
    # customization.plugins.core.bodyClass = 'customized'
    customization.plugins.core.title = ' '
    customization.plugins.core.faviconURL = '/resources/lmn_common/resources/img/favicon.png'
    customization.plugins.core.logoURL = '/resources/lmn_common/resources/img/logo-text-white.png'
    customization.plugins.core.bigLogoURL = '/resources/lmn_common/resources/img/logo-full.png'
    customization.plugins.core.hidePersonaLogin = true
    customization.plugins.core.enableMixpanel = false

angular.module('lmn.common').run ($localStorage) ->
    $localStorage.isWidescreen = true

angular.module('lmn.common').constant 'lmEncodingMap', {
    '': 'utf-8'
    'ascii': 'ascii'
    'utf8': 'utf-8'
    '8859-1': 'ISO8859-1'
    '8859-15': 'ISO8859-15'
    'win1252': 'cp1252'
}

$ () ->
    $('body').addClass('customized')
