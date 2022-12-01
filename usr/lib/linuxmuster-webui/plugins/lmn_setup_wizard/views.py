"""
Handles `setup.ini` file and finish the install process.
"""

import configparser
import os
import subprocess

from jadi import component
from aj.api.http import get, post, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.lmnfile import LMNFile


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/setup-wizard/setup')
    @endpoint(api=True, auth=True)
    def handle_api_read_setup(self, http_context):
        """
        Read settings from `/tmp/setup.ini`.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All setup settings
        :rtype: dict
        """

        if os.path.exists('/tmp/setup.ini'):
            with LMNFile('/tmp/setup.ini', 'r') as setup:
                return setup.data['setup']

    @post(r'/api/lmn/setup-wizard/setup')
    @endpoint(api=True, auth=True)
    def handle_api_write_setup(self, http_context):
        """
        Write setup config into `/tmp/setup.ini`.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        cfg = configparser.RawConfigParser()
        if os.path.exists('/tmp/setup.ini'):
            cfg.read('/tmp/setup.ini')

        if not cfg.has_section('setup'):
            cfg.add_section('setup')

        #cfg.remove_option('setup', 'opsiip')
        for key, value in http_context.json_body().items():
            if value == 'null':
                #raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(key))
                cfg.remove_option('setup', key)
            else:
                cfg.set('setup', key, str(value))

        #raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(cfg.items))

        with open('/tmp/setup.ini', 'w') as f:
            cfg.write(f)

    @get(r'/api/lmn/setup-wizard/is-configured')
    @endpoint(api=True)
    def handle_api_is_configured(self, http_context):
        """
        Test if linuxmuster was already configured by checking if the file
        `/var/lib/linuxmuster/setup.ini` exists.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Existence of `setup.ini`
        :rtype: bool
        """

        return os.path.exists('/var/lib/linuxmuster/setup.ini')

    @post(r'/api/lmn/setup-wizard/provision')
    @endpoint(api=True, auth=True)
    def handle_api_provision(self, http_context):
        """
        Launch `linuxmuster-setup` to configure all services.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        if http_context.json_body()['start'] == 'setup':
            try:
                subprocess.check_call(
                    'linuxmuster-setup -u -c /tmp/setup.ini >> /tmp/linuxmuster-setup.log & wait $! ',
                    shell=True
                )
            except Exception as e:
                raise EndpointError(None, message=str(e))
