import ConfigParser
import os
import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/setup-wizard/update-ini')
    @endpoint(api=True, auth=True)
    def handle_api_log(self, http_context, path=None):
        cfg = ConfigParser.RawConfigParser()
        if os.path.exists('/tmp/setup.ini'):
            cfg.read('/tmp/setup.ini')

        if not cfg.has_section('setup'):
            cfg.add_section('setup')

        for key, value in http_context.json_body().items():
            cfg.set('setup', key, str(value))

        with open('/tmp/setup.ini', 'w') as f:
            cfg.write(f)

    @url(r'/api/lm/setup-wizard/is-configured')
    @endpoint(api=True)
    def handle_api_is_configured(self, http_context):
        return os.path.exists('/var/lib/linuxmuster/setup.ini')

    @url(r'/api/lm/setup-wizard/provision')
    @endpoint(api=True, auth=True)
    def handle_api_provision(self, http_context):
        if http_context.method != 'POST':
            return
        try:
            subprocess.check_call(
                'linuxmuster-setup.py -u -c /tmp/setup.ini >> /tmp/linuxmuster-setup.log & ; wait $! && /usr/lib/linuxmuster-webui/plugins/lm_setup_wizard/template.sh',
                shell=True
            )
        except Exception as e:
            raise EndpointError(None, message=str(e))
