"""
API to load device file and run importing.
"""

import subprocess
from jadi import component
import os
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.lmnfile import LMNFile
from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_get_school_configpath
from aj.plugins.lmn_auth.api import School

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/devices')
    @authorize('lm:devices')
    @endpoint(api=True)
    def handle_api_devices(self, http_context):
        """
        Read and write the devices file.
        Method GET.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of config file in read mode.
        :rtype: string
        """
        
        
        school = School.get(self.context).school
        path = lmn_get_school_configpath(school)+'devices.csv'
        
        if os.path.isfile(path) is False:
            os.mknod(path)
        #path = '/etc/linuxmuster/sophomorix/default-school/devices.csv'
        fieldnames = [
            'room',
            'hostname',
            'group',
            'mac',
            'ip',
            'officeKey',
            'windowsKey',
            'dhcpOptions',
            'sophomorixRole',
            'lmnReserved10',
            'pxeFlag',
            'lmnReserved12',
            'lmnReserved13',
            'lmnReserved14',
            'sophomorixComment',
            'options',
        ]
        if http_context.method == 'GET':
            with LMNFile(path, 'r', fieldnames=fieldnames) as devices:
                return devices.read()

        if http_context.method == 'POST':
            data = http_context.json_body()
            for item in data:
                item.pop('_isNew', None)
                item.pop('null', None)
            with LMNFile(path, 'w', fieldnames=fieldnames) as f:
                f.write(data)

    @url(r'/api/lm/devices/import')
    @authorize('lm:devices:import')
    @endpoint(api=True)
    def handle_api_devices_import(self, http_context):
        """
        Launch the import of the devices in the system.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        try:
            subprocess.check_call('linuxmuster-import-devices > /tmp/import_devices.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))
