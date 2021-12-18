from aj.plugins.lmn_common.lmnfile import LMNFile
import subprocess
import re
import configparser
import pexpect

class SambaToolDNS():
    """
    Object to manage current samba dns entries on the system. 
    """

    def __init__(self):
        self._get_zone()
        if self.zone:
            self._get_credentials()
            self._get_ignore_list()

    def _get_credentials(self):
        """
        Load the credentials to use with samba-tool and store it in self.credentials.
        """

        with open('/etc/linuxmuster/.secret/administrator', 'r') as f:
            self.password = f.readline().strip('\n')

    def _get_zone(self):
        """
        Parse setup.ini to get the current zone and store it in self.zone.
        """

        # Used for pageTitle, see lmn_auth.api
        with LMNFile('/var/lib/linuxmuster/setup.ini', 'r') as setup:
            try:
                self.zone = setup.data['setup']['domainname']
            except KeyError:
                self.zone = ''

    def _get_ignore_list(self):
        """
        Get list of LMN devices to ignore them and store it in self.lmn_hosts,
        because the list of DNS entries would be too long.
        """

        path = '/etc/linuxmuster/sophomorix/default-school/devices.csv'
        fieldnames = [
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

        self.lmn_hosts = []
        with LMNFile(path, 'r', fieldnames=fieldnames) as devices:
            for device in devices.data:
                # Ignore comment lines
                if device['hostname'] is not None:
                    self.lmn_hosts.append(device['hostname'])

    def _samba_tool_process(self, action, options):
        """
        Execute samba-tool dns with parameter.

        :param action: query, add, delete or update
        :type action: string
        :param options: Tuple of necessary options for the query
        :type options: tuple
        :return: List of lines as strings
        :rtype: list
        """

        if action not in ['query', 'add', 'delete', 'update']:
            return

        cmd = ['samba-tool', 'dns', action, 'localhost', self.zone, *options, '-U', 'administrator']
        child = pexpect.spawn(' '.join(cmd))
        child.expect("Password for .*:")
        child.sendline(self.password)

        return child.read().decode().split('\r\n')

    def get_list(self):
        """
        Query all dns entries and parse it to sort it in a dict, but removes the devices entries.

        :return: Separate dns values from root and subdomains
        :rtype: dict
        """

        result = self._samba_tool_process('query', ('@', 'ALL'))

        # Filter results
        entries = {'root': [], 'sub': []}
        host = ''
        tmp_dict = {}
        types = ['AAAA', 'SOA', 'A', 'PTR', 'CNAME', 'NS', 'MX', 'TXT']
        for line in result:

            if "Name=," in line:
                # First header
                host = 'root'

            elif "Name=" in line:
                host = line.split("=")[1].split(',')[0].strip()
                if host in self.lmn_hosts:
                    host = ''

            elif host:
                for type in types:
                    if ' '+type+':' in line:
                        value = re.findall(': ([^(]*) \(', line)[0]
                        details = re.findall('\(([^)]*)\)', line)
                        if details[-1]:
                            options = dict(o.strip().split("=") for o in details[-1].split(','))
                        else:
                            options = {}
                        if type == "MX":
                            options['priority'] = details[0]
                        if host == 'root':
                            entries['root'].append(dict({'host':'','type':type,'value':value}, **options))
                        else:
                            entries['sub'].append(dict({'host':host,'type':type,'value':value}, **options))

        return entries

    def add(self, sub):
        """
        Add subdomain entry to dns.

        :param sub: Subdomain details
        :type sub: dict
        :return: Result of samba-tool
        :rtype: string
        """

        if sub['type'] == "MX":
            sub['value'] = sub['value'] + "\\ " + sub['priority']

        return self._samba_tool_process('add', (sub['host'], sub['type'], sub['value']))

    def update(self, old, new):
        """
        Update dns entry with new details.

        :param old: Old subdomain details
        :type old: dict
        :param new: New subdomain details
        :type new: dict
        :return: Result of samba-tool
        :rtype: string
        """

        if old['type'] == "MX":
            old['value'] = old['value'] + "\\ " + old['priority']
            new['value'] = new['value'] + "\\ " + new['priority']

        return self._samba_tool_process('update', (old['host'], old['type'], old['value'], new['value']))

    def delete(self, sub, type, entry):
        """
        Delete dns entry.

        :param sub: Subdomain
        :type sub: string
        :param type: Type of entry
        :type type: string
        :param entry: Value of the entry
        :type entry: string
        :return: Result of samba-tool
        :rtype: string
        """

        return self._samba_tool_process('delete', (sub, type, entry))
