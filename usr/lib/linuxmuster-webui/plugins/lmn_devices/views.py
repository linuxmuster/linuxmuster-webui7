"""
API to load device file and run importing.
"""

import subprocess
from jadi import component
import os
from aj.api.http import get, post, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.lmnfile import LMNFile
from aj.auth import authorize

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/devices')
    @authorize('lm:devices')
    @endpoint(api=True)
    def handle_api_get_devices(self, http_context):
        """
        Get all devices registered in devices.csv.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of config file in read mode.
        :rtype: string
        """

        path = f'{self.context.schoolmgr.configpath}devices.csv'

        if os.path.isfile(path) is False:
            os.mknod(path)

        with LMNFile(path, 'r') as devices:
            return devices.read()

    @post(r'/api/lmn/devices')
    @authorize('lm:devices')
    @endpoint(api=True)
    def handle_api_post_devices(self, http_context):
        """
        Write all devices in devices.csv.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of config file in read mode.
        :rtype: string
        """

        path = f'{self.context.schoolmgr.configpath}devices.csv'

        if os.path.isfile(path) is False:
            os.mknod(path)

        data = http_context.json_body()
        for item in data:
            item.pop('_isNew', None)
            item.pop('null', None)
        with LMNFile(path, 'w') as f:
            f.write(data)

    @post(r'/api/lmn/devices/import')
    @authorize('lm:devices:import')
    @endpoint(api=True)
    def handle_api_devices_import(self, http_context):
        """
        Launch the import of the devices in the system.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        school = self.context.schoolmgr.school
        try:
            subprocess.check_call('linuxmuster-import-devices -s '+ school +' > /tmp/import_devices.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))
