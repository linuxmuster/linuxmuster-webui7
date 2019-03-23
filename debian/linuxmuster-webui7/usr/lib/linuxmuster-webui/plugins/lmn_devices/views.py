import csv
import subprocess
import os

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.api import CSVSpaceStripper
from aj.plugins.lmn_common.api import lmn_backup_file
from aj.plugins.lmn_common.api import lmn_list_backup_file, lmn_restore_backup_file
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
            lmn_backup_file(path)
            with open(path, 'w') as f:
                csv.DictWriter(f, delimiter=';', fieldnames=fieldnames).writerows(data)

    @url(r'/api/lm/devices/import')
    @authorize('lm:devices:import')
    @endpoint(api=True)
    def handle_api_devices_import(self, http_context):
        try:
            subprocess.check_call('linuxmuster-import-devices > /tmp/import_devices.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))
            
    @url(r'/api/lm/devices-backup')
    @authorize('lm:devices')
    @endpoint(api=True)
    def handle_api_devices_backup(self, http_context):
        path = '/etc/linuxmuster/sophomorix/default-school/devices.csv'
        return lmn_list_backup_file(path)
        
    @url(r'/api/lm/devices-restore')
    @authorize('lm:devices')
    @endpoint(api=True)
    def handle_api_devices_restore(self, http_context):
        if http_context.method == 'POST':
            backupfile = '/etc/linuxmuster/sophomorix/default-school/' + http_context.json_body()['backupfile']
            path = '/etc/linuxmuster/sophomorix/default-school/devices.csv'
            return lmn_restore_backup_file(path, backupfile)

    @url(r'/api/lm/remove-backup')
    @authorize('lm:devices')
    @endpoint(api=True)
    def handle_api_remove_backup(self, http_context):
        if http_context.method == 'POST':
            backupfile = '/etc/linuxmuster/sophomorix/default-school/' + http_context.json_body()['backupfile']
            if not os.path.exists(backupfile):
                return
            else:
                os.unlink(backupfile)
                return True
