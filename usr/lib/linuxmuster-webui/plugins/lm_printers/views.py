import psutil

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lm_common.api import lm_backup_file


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/printers')
    @authorize('lm:printers')
    @endpoint(api=True)
    def handle_api_printers(self, http_context):
        access_path = '/etc/cups/access.conf'
        printers_path = '/etc/cups/printers.conf'
        if http_context.method == 'GET':
            result = []
            found_names = []
            for line in open(access_path):
                if line.startswith('<Location'):
                    printer = {
                        'name': line.split()[-1].rstrip(' >').split('/')[-1],
                        'items': []
                    }
                    found_names.append(printer['name'])
                    result.append(printer)
                if line.strip().startswith('Allow From'):
                    printer['items'].append(line.strip().split()[-1])
            for line in open(printers_path):
                if line.startswith('<Printer'):
                    printer = {
                        'name': line.split()[-1].rstrip(' >').split('/')[-1],
                        'items': []
                    }
                    if printer['name'] not in found_names:
                        result.append(printer)
            return result
        if http_context.method == 'POST':
            content = ''
            for printer in http_context.json_body():
                if len(printer['items']) == 0:
                    continue
                content += '<Location /printers/%s>\n' % printer['name']
                content += '\tOrder Deny,Allow\n'
                content += '\tDeny From All\n'
                for item in printer['items']:
                    content += '\tAllow From %s\n' % item

                for v in psutil.net_if_addrs().values():
                    for x in v:
                        if not ':' in x.address:
                            content += '\tAllow From %s\n' % x.address

                content += '</Location>\n'

            lm_backup_file(access_path)
            with open(access_path, 'w') as f:
                f.write(content)
