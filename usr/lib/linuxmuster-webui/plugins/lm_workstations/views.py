import csv
import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lm_common.api import CSVSpaceStripper
from aj.plugins.lm_common.api import lm_backup_file
from aj.auth import authorize


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/workstations')
    @authorize('lm:workstations')
    @endpoint(api=True)
    def handle_api_workstations(self, http_context):
        path = '/etc/linuxmuster/sophomorix/default-school/devices.csv'
        fieldnames = [
            'room',
            'hostname',
            'group',
            'mac',
            'ip',
            'officeKey',
            'windowsKey',
            'lmnReserved',
            'userReserved',
            'accountType',
            'pxeFlag',
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
            lm_backup_file(path)
            with open(path, 'w') as f:
                csv.DictWriter(f, delimiter=';', fieldnames=fieldnames).writerows(data)

    @url(r'/api/lm/workstations/import')
    @authorize('lm:workstations:import')
    @endpoint(api=True)
    def handle_api_workstations_import(self, http_context):
        try:
            subprocess.check_call('linuxmuster-import-devices.py > /tmp/import_workstations.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))
