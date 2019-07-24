# coding=utf-8
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/quota/')
    @endpoint(api=True)
    def handle_api_quota(self, http_context):

       if http_context.method == 'POST':

                user = self.context.identity

                if user != 'root':
                    sophomorixCommand = ['sophomorix-query', '--sam', user, '--user-full', '--quota-usage', '-jj']
                    jsonpath          = 'USER/' + user + '/QUOTA_USAGE_BY_SHARE/linuxmuster-global'
                    result            = lmn_getSophomorixValue(sophomorixCommand, jsonpath)
                    if result['HARD_LIMIT_MiB'] == 'NO LIMIT':
                        return {
                            'used': result['USED_MiB'],
                            #'free':  'Unlimited', ## free not used yet
                            'total': 'Unlimited'
                        }
                    else:

                        return {
                            'used': result['USED_MiB'],
                            #'free': result['HARD_LIMIT_MiB']-result['USED_MiB'],
                            'total': result['HARD_LIMIT_MiB']
                        }
                else:
                    return {
                        'used': 0,
                        #'free': 0,
                        'total': 1
                    }
