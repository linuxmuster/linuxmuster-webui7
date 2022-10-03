"""
Module to drive some workstations through linbo.
"""

from jadi import component

import sys
sys.path.append('/srv/tmp')

from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_linbo_sync import api

## TODO
# Better icons and design
# Force some options even if not present in start.conf ?

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/linbosync/last_syncs')
    @authorize('lm:sync:list')
    @endpoint(api=True)
    def handle_api_linbo_sync(self, http_context):
        """
        Get the last synchronisation date from all workstations.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Workstations dict with all linbo informations
        :rtype: dict or list
        """

        workstations = api.list_workstations(self.context)
        api.last_sync_all(workstations)

        if len(workstations) != 0:
            return workstations
        else:
            return ["none"]

    @get(r'/api/lmn/linbosync/isOnline/(?P<host>[\w\-]+)')
    @endpoint(api=True)
    @authorize('lm:sync:online')
    def handle_api_workstations_online(self, http_context, host):
        """
        Connector to test if a host is online.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param host: Hostname
        :type host: string
        :return: OS type if online, or off
        :rtype: string
        """

        return api.test_online(host)

    @post(r'/api/lmn/linbosync/run')
    @endpoint(api=True)
    @authorize('lm:sync:sync')
    def handle_api_sync_workstation(self, http_context):
        """
        Connector to launch a linbo command.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Error as string if down, or 0 if successfull
        :rtype: string or integer 0
        """

        cmd = http_context.json_body()['cmd']
        return api.run(cmd.split())
