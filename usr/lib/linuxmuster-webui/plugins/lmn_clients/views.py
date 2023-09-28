from jadi import component
import os
import logging
import string
import xml.etree.ElementTree as ElementTree

from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import samba_realm
from aj.plugins.lmn_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/clients/scripts')
    @authorize('lmn:clients:config')
    @endpoint(api=True)
    def handle_api_get_clients_scripts(self, http_context):

        def read_script_content(path):
            if os.path.isfile(path):
                with open(path, 'r') as script:
                    content = script.read()
                return content
            logging.warning(f'{path} does not exists !')
            return ""

        if samba_realm is None:
            logging.error(_('Unable to determine samba domain'))
            return {}

        school = self.context.schoolmgr.school

        custom_script_path = f'/var/lib/samba/sysvol/{samba_realm}/scripts/{school}/custom/'
        scripts_linux = ['sessionstart.sh', 'logon.sh', 'sysstart.sh', 'sysstop.sh']
        scripts_windows = ['logoff.bat', 'logon.bat', 'sysstart.bat', 'sysstop.bat']

        return {
            'path': custom_script_path,
            'linux': [
                {
                    'path':f'{custom_script_path}/linux/{script}',
                    'name': script,
                    'content': read_script_content(f'{custom_script_path}/linux/{script}'),
                } for script in scripts_linux
            ],
            'windows': [
                {
                    'path': f'{custom_script_path}/windows/{script}',
                    'name': script,
                    'content': read_script_content(f'{custom_script_path}/windows/{script}'),
                } for script in scripts_windows
            ],
        }

    @post(r'/api/lmn/clients/scripts')
    @authorize('lmn:clients:config')
    @endpoint(api=True)
    def handle_api_write_clients_scripts(self, http_context):

        path = http_context.json_body()['path']
        content = http_context.json_body()['content']

        try:
            with open(path, 'w') as script:
                script.write(content)
        except FileNotFoundError:
            http_context.respond_not_found()
            return


    @get(r'/api/lmn/samba/drives')
    @authorize('lmn:clients:config')
    @endpoint(api=True)
    def handle_api_get_samba_drives(self, http_context):

        self.context.schoolmgr.drivemgr.load()
        drives = self.context.schoolmgr.drivemgr.aslist()
        usedLetters = self.context.schoolmgr.drivemgr.usedLetters

        availableDriveLetters = [ {
            'letter': l,
            'active': False if l not in usedLetters else True,
            }
            for l in list(string.ascii_letters[26:])
        ]

        return drives, availableDriveLetters

    @post(r'/api/lmn/samba/drives')
    @authorize('lmn:clients:config')
    @endpoint(api=True)
    def handle_api_post_samba_drives(self, http_context):

        drives_config = http_context.json_body()['drives']
        self.context.schoolmgr.drivemgr.save(drives_config)

