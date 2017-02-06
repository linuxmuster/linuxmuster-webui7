import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import authorize
from aj.plugins.lm_common.api import lm_backup_file


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/room-defaults')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_room_defaults(self, http_context):
        path = '/etc/linuxmuster/room_defaults'
        fieldnames = [
            'id',
            'internet',
            'intranet',
            'webfilter',
        ]
        if http_context.method == 'GET':
            data = list(
                dict(zip(fieldnames, line.split()[:4]))
                for line in open(path)
                if line.strip() and not line.startswith('#')
            )
            for x in data:
                for k in fieldnames[1:]:
                    x[k] = {
                        'on': True,
                        'off': False,
                        '-': data[0][k],
                    }[x[k]]
            return data
        if http_context.method == 'POST':
            data = http_context.json_body()
            lm_backup_file(path)
            with open(path, 'w') as f:
                f.write(''.join(
                    (x['id'] + ' ' + ' '.join('on' if x[k] else 'off' for k in fieldnames[1:]) + '\n')
                    for x in data
                ))

    @url(r'/api/lm/room-defaults/apply')
    @authorize('lm:quotas:apply')
    @endpoint(api=True)
    def handle_api_room_defaults_apply(self, http_context):
        try:
            subprocess.check_call('linuxmuster-reset --all > /tmp/apply-room-defaults.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))

    @url(r'/api/lm/edv-rooms')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_edv_rooms(self, http_context):
        path = '/etc/linuxmuster/classrooms'
        if http_context.method == 'GET':
            return list(
                line.strip()
                for line in open(path)
                if line.strip() and not line.startswith('#')
            )
        if http_context.method == 'POST':
            data = http_context.json_body()
            lm_backup_file(path)
            with open(path, 'w') as f:
                f.write(''.join(
                    x + '\n'
                    for x in data
                ))
