angular.module 'lm.common', [
    'core',
    'ajenti.ace',
    'ajenti.filesystem',
]

angular.module('lm.common').run (customization) ->
    customization.plugins.core.startupURL = ''
    # customization.plugins.core.bodyClass = 'customized'
    customization.plugins.core.title = ' '
    customization.plugins.core.faviconURL = '/resources/lm_common/resources/img/favicon.png'
    customization.plugins.core.logoURL = '/resources/lm_common/resources/img/logo-small.png'
    customization.plugins.core.bigLogoURL = '/resources/lm_common/resources/img/logo-full.png'
    customization.plugins.core.hidePersonaLogin = true

angular.module('lm.common').constant 'lmEncodingMap', {
    '': 'utf-8'
    'ascii': 'ascii'
    'utf8': 'utf-8'
    '8859-1': 'ISO8859-1'
    '8859-15': 'ISO8859-15'
    'win1252': 'cp1252'
}

$ () ->
    $('body').addClass('customized')
