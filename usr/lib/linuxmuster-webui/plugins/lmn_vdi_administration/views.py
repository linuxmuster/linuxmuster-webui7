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

    @get(r'/api/lmn/vdi/administration/masterVMs')
    # Set the right permissions if necessary, see main.py to activate it.
    #@authorize('lmn_vdi_administration:show')
    @endpoint(api=True)
    def handle_api_lmn_vdi_administration_master(self, http_context):

        path = "/usr/lib/linuxmuster-linbo-vdi"
        if os.path.isdir(path) == False and os.path.islink(path) == False:
            return { "status": "error", "message": "VDI Tools not installed!" }

        getVmStatesCommand=['sudo', '/usr/lib/linuxmuster-linbo-vdi/getVmStates.py', '-master']
        output = subprocess.check_output(getVmStatesCommand, shell=False)
        output_new = ""
        for line in output.decode().splitlines():
            if line.find("*") == -1:
                output_new += line + "\n"
        vmStates = json.loads(output_new)
        return { "status": "success", "data": vmStates }


    @get(r'/api/lmn/vdi/administration/clones')
    # Set the right permissions if necessary, see main.py to activate it.
    #@authorize('lmn_vdi_administration:show')
    @endpoint(api=True)
    def handle_api_lmn_vdi_administration_clone(self, http_context):

        path = "/usr/lib/linuxmuster-linbo-vdi"
        if os.path.isdir(path) == False and os.path.islink(path) == False:
            return { "status": "error", "message": "VDI Tools not installed!" }

        getClonesCommand=['sudo', '/usr/lib/linuxmuster-linbo-vdi/getVmStates.py', '-clones']
        output = subprocess.check_output(getClonesCommand, shell=False)
        output_new = ""
        for line in output.decode().splitlines():
            if line.find("*") == -1:
                output_new += line + "\n"
        clones = json.loads(output_new)
        return { "status": "success", "data": clones }
