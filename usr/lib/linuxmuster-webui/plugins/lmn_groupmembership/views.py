# coding=utf-8
import os
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lm_common.api import lm_backup_file
from aj.plugins.lm_common.api import lmn_getSophomorixValue
from configparser import ConfigParser



@component(HttpPlugin)
class Handler(HttpPlugin):

    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/groupmembership')
    @authorize('lmn:groupmembership')
    @endpoint(api=True)
    def handle_api_settings(self, http_context):
        schoolname = 'default-school'
        username = 'hulk'
        if http_context.method == 'GET':
            sophomorixCommand = ['sophomorix-query',  '--schoolbase', schoolname, '--user-full', '-j', '--sam', username]
            usergroups = lmn_getSophomorixValue(sophomorixCommand, 'USER/'+username+'memberOf')

            sophomorixCommand = ['sophomorix-query', '--class', '--schoolbase', schoolname, '--group-full', '-jj']
            classes = lmn_getSophomorixValue(sophomorixCommand, 'GROUP')
            # Parse csv config file
            return classes


        if http_context.method == 'POST':
            content = ''
            data = http_context.json_body()
            if 'admins_print' in data:
                for k, v in self.EMAIL_MAPPING.items():
                    data['admins_print'] = data['admins_print'].replace(k, v)

            def convert_value(v):
                if type(v) is int:
                    return str(v)
                elif type(v) is bool:
                    return 'yes' if v else 'no'
                else:
                    return '%s' % v


