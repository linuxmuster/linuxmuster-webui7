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

    @url(r'/api/lmn/landing')
    @authorize('lmn:landing')
    @endpoint(api=True)
    def handle_api_settings(self, http_context):
        schoolname = 'default-school'
        username = http_context.json_body()['username']
        action = http_context.json_body()['action']

    @url(r'/api/lmn/quota/') ## TODO authorize
    @endpoint(api=True)
    def handle_api_quota(self, http_context):
       if http_context.method == 'POST':
            #with authorize('lm:users:students:write'): ## TODO
                
                user = self.context.identity
                
                if user != 'root':
                    sophomorixCommand = ['sophomorix-query', '--sam', user, '--user-full', '--quota-usage', '-jj']
                    jsonpath          = 'USER/' + user + '/QUOTA_USAGE_BY_SHARE/linuxmuster-global'
                    result            = lmn_getSophomorixValue(sophomorixCommand, jsonpath)
                    print("#"*50, user, result, self.context.identity)
                    return {
                        'used': result['USED_MiB'],
                        'free': result['HARD_LIMIT_MiB']-result['USED_MiB'],
                        'total': result['HARD_LIMIT_MiB']
                    }
                else:
                    return {
                        'used': 0,
                        'free': 0,
                        'total': 1
                    }
