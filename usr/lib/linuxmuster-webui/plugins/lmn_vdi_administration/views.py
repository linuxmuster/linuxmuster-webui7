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
            if os.path.isdir(path) == False:
                return { "status": "error", "message": "VDI Tools not installed!" }

            action = http_context.json_body()['action']
            if action == 'get-masterVMs':
                getVmStatesCommand=['/usr/lib/linuxmuster-linbo-vdi/getVmStates.py', '-master']
                output = subprocess.check_output(getVmStatesCommand, shell=False)
                output_new = ""
                for line in output.decode().splitlines():
                    if line.find("*") == -1:
                        output_new += line + "\n"
                vmStates = json.loads(output_new)
                return { "status": "success", "data": vmStates }
                #return vmStates
            
            if action == 'get-clones':
                getClonesCommand=['/usr/lib/linuxmuster-linbo-vdi/getVmStates.py', '-clones']
                output = subprocess.check_output(getClonesCommand, shell=False)
                output_new = ""
                for line in output.decode().splitlines():
                    if line.find("*") == -1:
                        if line.find("[") == -1:
                            if line != "{}":
                                output_new += line + "\n"
                clones = json.loads(output_new)
                return { "status": "success", "data": clones }
                #return clones
 

