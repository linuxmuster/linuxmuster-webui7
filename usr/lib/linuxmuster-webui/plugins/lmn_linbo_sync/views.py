"""
Module to drive some workstations through linbo.
"""

import logging
import subprocess
import time
from datetime import datetime
from jadi import component

import sys
sys.path.append('/srv/tmp')

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_linbo_sync import api

## TODO
# Add initcache and partition
# Add option -p
# Delete option -w if timeout is 0
# Better icons and design
# Force some options even if not present in start.conf ?

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/linbo/SyncList')
    @authorize('lm:sync:list')
    @endpoint(api=True)
    def handle_api_linbo_sync(self, http_context):
        """
        Get the last synchronisation date from all workstations.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Workstations dict with all linbo informations
        :rtype: dict or list
        """

        if http_context.method == 'GET':
            workstations = api.list_workstations(self.context)
            api.last_sync_all(workstations)

            if len(workstations) != 0:
                return workstations
            else:
                return ["none"]

    @url(r'/api/lm/linbo/isOnline/(?P<host>[\w\-]+)')
    @endpoint(api=True)
    @authorize('lm:sync:online')
    def handle_api_workstations_online(self, http_context, host):
        """
        Connector to test if a host is online.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param host: Hostname
        :type host: string
        :return: OS type if online, or off
        :rtype: string
        """

        if http_context.method == 'GET':
            return api.test_online(host)

    @url(r'/api/lm/linbo/run')
    @endpoint(api=True)
    @authorize('lm:sync:sync')
    def handle_api_sync_workstation(self, http_context):
        """
        Connector to launch a linbo command.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Error as string if down, or 0 if successfull
        :rtype: string or integer 0
        """

        action = http_context.json_body()['action']

        if http_context.method == 'POST':
            if action == 'run-linbo':
                cmd = http_context.json_body()['cmd']
                return api.run(cmd.split())
