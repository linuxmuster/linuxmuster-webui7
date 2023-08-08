"""
Module to handle dchp leases and eventually add a new device.
"""

from jadi import component
from isc_dhcp_leases import Lease, IscDhcpLeases

from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.lmnfile import LMNFile

@component(HttpPlugin)
class Handler(HttpPlugin):

    def __init__(self, context):
        self.context = context
        self.path = '/etc/linuxmuster/sophomorix/default-school/devices.csv'

    @get(r'/api/lmn/dhcp/leases')
    @authorize('lm:devices')
    @endpoint(api=True)
    def handle_api_get_dhcp(self, http_context):
        """
        Read dhcp lease file and sort it for each LMN devices.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All lease and LMN devices ip details
        :rtype: tuple of dict
        """

        pathLease = '/var/lib/dhcp/dhcpd.leases'

        leases = IscDhcpLeases(pathLease)
        data = []
        for mac, details in leases.get_current().items():
            data.append({
                'mac': mac,
                'ip': details.ip,
                'starts': details.start.strftime("%A, %d. %B %Y %H:%M:%S"),
                'ends': details.end.strftime("%A, %d. %B %Y %H:%M:%S"),
            })

        used = []
        with LMNFile(self.path, 'r') as devices:
            for host in devices.read():
                if host["hostname"] != None and \
                   host["mac"] != None and \
                   host["ip"] != None and \
                   host["room"][0] != "#":
                    used.append({
                        'mac':host['mac'],
                        'ip': host['ip'],
                        'hostname': host['hostname'],
                    })
        return data, used

    @post(r'/api/lmn/dhcp/register')
    @authorize('lm:devices:import')
    @endpoint(api=True)
    def handle_api_register_dhcp(self, http_context):
        """
        When a new device get an ip through dhcp, this method allows to register it in the LMN devices file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Success
        :rtype: bool
        """

        new_device = http_context.json_body()['device']
        with LMNFile(self.path, 'w+') as devices:
            content = devices.read()
            content.append(new_device)
            devices.write(content)
        return True
