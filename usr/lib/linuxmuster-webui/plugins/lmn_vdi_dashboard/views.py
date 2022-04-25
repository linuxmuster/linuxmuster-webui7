from jadi import component

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

import subprocess
import json
import os

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn_vdi_dashboard')
    @endpoint(api=True)
    def handle_api_example_lmn_vdi_dashboard(self, http_context):
        if http_context.method == 'POST':
            action = http_context.json_body()['action']
            if action == 'get-vdiSession':
                username = http_context.json_body()['username']
                group = http_context.json_body()['group']
                createSessionCommand = ['sudo', '/usr/lib/linuxmuster-linbo-vdi/getConnection.py', group, username]
                output = subprocess.check_output(createSessionCommand, shell=False)
                output = json.loads(output.decode())
                return output['configFile'].split("/")[3]

    @url(r'/api/lmn_vdi_dashboard/download/(?P<name>.+)')
    @endpoint(api=False, page=True)
    def handle_api_download_config(self, http_context, name=None):
        path = "/tmp/vdi/" + name
        if os.path.isfile(path):
            return http_context.file(path, inline=False, name=b'vdi-session.vv')
        else:
            return http_context.respond_forbidden()
        
