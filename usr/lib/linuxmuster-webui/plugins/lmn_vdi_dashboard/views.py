from jadi import component

from aj.api.http import get, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

import subprocess
import json
import os

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/vdi/dashboard/vdiSession/(?P<group>.+)')
    @endpoint(api=True)
    def handle_api_lmn_vdi_dashboard_session(self, http_context, group):
        username = self.context.identity
        createSessionCommand = ['sudo', '/usr/lib/linuxmuster-linbo-vdi/getConnection.py', group, username]
        output = subprocess.check_output(createSessionCommand, shell=False)
        output = json.loads(output.decode())
        return output['configFile'].split("/")[3]

    @get(r'/api/lmn/vdi/dashboard/download/(?P<name>.+)')
    @endpoint(api=False, page=True)
    def handle_api_download_config(self, http_context, name=None):
        path = "/tmp/vdi/" + name
        if os.path.isfile(path):
            return http_context.file(path, inline=False, name=b'vdi-session.vv')
        else:
            return http_context.respond_forbidden()

