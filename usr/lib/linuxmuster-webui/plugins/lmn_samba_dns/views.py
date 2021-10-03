"""
Module to handle the samba dns through samba-tool.
"""

from jadi import component

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_samba_dns.smbtool import SambaToolDNS

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        try:
            self.dns = SambaToolDNS() # Context !
        except PermissionError:
            self.dns = None

    @url(r'/api/dns/get')
    @authorize('lm:samba_dns:read')
    @endpoint(api=True)
    def handle_api_dns_get(self, http_context):
        """
        Deliver the current dns entries and dns zone.
        Method GET.
        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of dns entries and zone
        :rtype: list
        """

        if http_context.method == 'GET':
            return [self.dns.get_list(), self.dns.zone]

    @url(r'/api/dns/delete')
    @authorize('lm:samba_dns:write')
    @endpoint(api=True)
    def handle_api_dns_delete(self, http_context):
        """
        Send entry to delete to samba-tool.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Result of samba-tool
        :rtype: string
        """

        if http_context.method == 'POST':
            sub = http_context.json_body()['sub']
            t = http_context.json_body()['type']
            value = http_context.json_body()['value']
            return self.dns.delete(sub, t, value)

    @url(r'/api/dns/add')
    @authorize('lm:samba_dns:write')
    @endpoint(api=True)
    def handle_api_dns_add(self, http_context):
        """
        Send dns entry to add to samba-tool.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Result of samba-tool
        :rtype: string
        """

        if http_context.method == 'POST':
            sub = http_context.json_body()['sub']
            return self.dns.add(sub)

    @url(r'/api/dns/update')
    @authorize('lm:samba_dns:write')
    @endpoint(api=True)
    def handle_api_dns_update(self, http_context):
        """
        Send dns entry to update to samba-tool.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Result of samba-tool
        :rtype: string
        """

        if http_context.method == 'POST':
            old = http_context.json_body()['old']
            new = http_context.json_body()['new']
            return self.dns.update(old, new)
