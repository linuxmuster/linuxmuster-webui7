"""
Module to handle dchp leases and eventually add a new device.
"""

from jadi import component
from isc_dhcp_leases import Lease, IscDhcpLeases

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.lmnfile import LMNFile

@component(HttpPlugin)
class Handler(HttpPlugin):

    def __init__(self, context):
        self.context = context
        self.path = '/etc/linuxmuster/sophomorix/default-school/devices.csv'
        self.fieldnames = [
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

    @url(r'/api/get-dhcp')
    #@authorize('extra_dhcp:show')
    @endpoint(api=True)
    def handle_api_get_dhcp(self, http_context):
        """
        Read dhcp lease file and sort it for each LMN devices.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All lease and LMN devices ip details
        :rtype: tuple of dict
        """

        pathLease = '/var/lib/dhcp/dhcpd.leases'

        if http_context.method == 'GET':
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
            with LMNFile(self.path, 'r', fieldnames=self.fieldnames) as devices:
                for host in devices.read():
                    if host["hostname"] != None or host["mac"] != None:
                        used.append({
                            'mac':host['mac'],
                            'ip': host['ip'],
                            'hostname': host['hostname'],
                        })
            return data, used

    @url(r'/api/register-dhcp')
    #@authorize('extra_dhcp:show')
    @endpoint(api=True)
    def handle_api_register_dhcp(self, http_context):
        """
        When a new device get an ip through dhcp, this method allows to register it in the LMN devices file.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Success
        :rtype: bool
        """

        if http_context.method == 'POST':
            new_device = http_context.json_body()['device']
            with LMNFile(self.path, 'w+', fieldnames=self.fieldnames) as devices:
                content = devices.read()
                content.append(new_device)
                devices.write(content)
            return True