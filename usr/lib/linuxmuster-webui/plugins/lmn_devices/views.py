import unicodecsv as csv
import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.api import CSVSpaceStripper, lmn_write_csv
from aj.auth import authorize


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/devices')
    @authorize('lm:devices')
    @endpoint(api=True)
    def handle_api_devices(self, http_context):
        path = '/etc/linuxmuster/sophomorix/default-school/devices.csv'
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
            return list(
                csv.DictReader(CSVSpaceStripper(open(path)), delimiter=';', fieldnames=fieldnames)
            )
        if http_context.method == 'POST':
            data = http_context.json_body()
            for item in data:
                item.pop('_isNew', None)
                item.pop('null', None)
            lmn_write_csv(path, fieldnames, data)

    @url(r'/api/lm/devices/import')
    @authorize('lm:devices:import')
    @endpoint(api=True)
    def handle_api_devices_import(self, http_context):
        try:
            subprocess.check_call('linuxmuster-import-devices > /tmp/import_devices.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))
