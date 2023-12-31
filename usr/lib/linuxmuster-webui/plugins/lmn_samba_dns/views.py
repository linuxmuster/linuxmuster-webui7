"""
Module to handle the samba dns through samba-tool.
"""

from jadi import component

from aj.api.http import get, post, delete, put, patch, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from linuxmusterTools.samba_util import SambaToolDNS

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        try:
            self.dns = SambaToolDNS() # Context !
        except PermissionError:
            self.dns = None

    @get(r'/api/lmn/dns')
    @authorize('lm:samba_dns:read')
    @endpoint(api=True)
    def handle_api_dns_get(self, http_context):
        """
        Deliver the current dns entries and dns zone.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of dns entries and zone
        :rtype: list
        """

        return [self.dns.list(), self.dns.zone]

    @patch(r'/api/lmn/dns')
    @authorize('lm:samba_dns:write')
    @endpoint(api=True)
    def handle_api_dns_delete(self, http_context):
        """
        Send entry to delete to samba-tool.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Result of samba-tool
        :rtype: string
        """

        sub = http_context.json_body()['sub']
        t = http_context.json_body()['type']
        value = http_context.json_body()['value']
        return self.dns.delete(sub, t, value)

    @put(r'/api/lmn/dns')
    @authorize('lm:samba_dns:write')
    @endpoint(api=True)
    def handle_api_dns_add(self, http_context):
        """
        Send dns entry to add to samba-tool.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Result of samba-tool
        :rtype: string
        """

        sub = http_context.json_body()['sub']
        return self.dns.add(sub)

    @post(r'/api/lmn/dns')
    @authorize('lm:samba_dns:write')
    @endpoint(api=True)
    def handle_api_dns_update(self, http_context):
        """
        Send dns entry to update to samba-tool.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Result of samba-tool
        :rtype: string
        """

        old = http_context.json_body()['old']
        new = http_context.json_body()['new']
        return self.dns.update(old, new)
