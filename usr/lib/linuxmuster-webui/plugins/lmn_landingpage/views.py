# coding=utf-8
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lm_common.api import lmn_getSophomorixValue

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

    @url(r'/api/lmn/quota/(?P<user>\w+)') ## TODO authorize
    @endpoint(api=True)
    def handle_api_quota(self, http_context, user):
        
        v = {'total': 2147483648, 'used':62914560} ## TODO how to get values from sophomorix-quota
        return {
            'used': v['used'],
            'free': v['total']-v['used'],
            'total': v['total']
        }
