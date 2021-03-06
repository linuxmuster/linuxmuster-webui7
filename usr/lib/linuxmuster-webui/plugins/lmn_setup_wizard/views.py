"""
Handles `setup.ini` file and finish the install process.
"""

import configparser
import os
import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/setup-wizard/read-ini')
    @endpoint(api=True, auth=True)
    def handle_api_read_log(self, http_context):
        """
        Read settings from `/tmp/setup.ini`.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All setup settings
        :rtype: dict
        """

        config = configparser.RawConfigParser()
        if http_context.method == 'GET':
            if os.path.exists('/tmp/setup.ini'):
                config.read('/tmp/setup.ini')
                settings = {}
                # iterate all sections
                for section in config.sections():
                    for (key, val) in config.items(section):
                        # Translate types
                        if val.isdigit():
                            val = int(val)
                        if val == 'no':
                            val = False
                        if val == 'yes':
                            val = True
                        if val == 'True':
                            val = True
                        if val == 'False':
                            val = False
                        settings[key] = val
                return settings

    @url(r'/api/lm/setup-wizard/update-ini')
    @endpoint(api=True, auth=True)
    def handle_api_log(self, http_context):
        """
        Write setup config into `/tmp/setup.ini`.
        Method POST.

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

    @url(r'/api/lm/setup-wizard/is-configured')
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

    @url(r'/api/lm/setup-wizard/provision')
    @endpoint(api=True, auth=True)
    def handle_api_provision(self, http_context):
        """
        Launch `linuxmuster-setup` to configure all services.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        if http_context.method != 'POST':
            return
        if http_context.json_body()['start'] == 'setup':
            try:
                subprocess.check_call(
                    'linuxmuster-setup -u -c /tmp/setup.ini >> /tmp/linuxmuster-setup.log & wait $! ',
                    shell=True
                )
            except Exception as e:
                raise EndpointError(None, message=str(e))

    @url(r'/api/lm/setup-wizard/restart') ## TODO : Handle maybe obsolet
    @endpoint(api=True, auth=True)
    def handle_api_restart(self, http_context):
        """
        Restart webui service after setup is finished (to switch to https).

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        if http_context.method != 'POST':
            return
        try:
            subprocess.check_call(
                'systemctl restart linuxmuster-webui.service',
                shell=True
            )
        except Exception as e:
            raise EndpointError(None, message=str(e))
