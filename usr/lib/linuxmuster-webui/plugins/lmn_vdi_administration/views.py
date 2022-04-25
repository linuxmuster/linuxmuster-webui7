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

    @url(r'/api/lmn_vdi_administration')
    # Set the right permissions if necessary, see main.py to activate it.
    #@authorize('lmn_vdi_administration:show')
    @endpoint(api=True)
    def handle_api__lmn_vdi_administration(self, http_context):
        if http_context.method == 'POST':

            path = "/usr/lib/linuxmuster-linbo-vdi"
            if os.path.isdir(path) == False and os.path.islink(path) == False:
                return { "status": "error", "message": "VDI Tools not installed!" }

            action = http_context.json_body()['action']
            if action == 'get-masterVMs':
                getVmStatesCommand=['sudo', '/usr/lib/linuxmuster-linbo-vdi/getVmStates.py', '-master']
                output = subprocess.check_output(getVmStatesCommand, shell=False)
                vmStates = json.loads(output)
                return { "status": "success", "data": vmStates }

            if action == 'get-clones':
                getClonesCommand=['sudo', '/usr/lib/linuxmuster-linbo-vdi/getVmStates.py', '-clones']
                output = subprocess.check_output(getClonesCommand, shell=False)
                clones = json.loads(output)
                return { "status": "success", "data": clones }
 

