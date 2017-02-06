# coding=utf-8
import os
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lm_common.api import lm_backup_file


@component(HttpPlugin)
class Handler(HttpPlugin):
    EMAIL_MAPPING = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss',
        '@': '\\@',
    }
    EMAIL_REVERSE_MAPPING = dict(
        (v, k) for (k, v) in EMAIL_MAPPING.items()
    )

    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/settings')
    @authorize('lm:settings')
    @endpoint(api=True)
    def handle_api_settings(self, http_context):
        path = '/etc/sophomorix/user/sophomorix.conf'
        if http_context.method == 'GET':
            result = {}
            for line in open(path):
                if line.startswith(('$', '#$')):
                    line = line.strip().lstrip('#$').rstrip(';')
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip()

                    if v[0] == '"':
                        v = v.strip('"')
                        v = {'yes': True, 'no': False}.get(v, v)
                    else:
                        v = int(v)

                    result[k] = v

            if 'admins_print' in result:
                for k, v in self.EMAIL_REVERSE_MAPPING.items():
                    result['admins_print'] = result['admins_print'].replace(k, v)
            return result
        if http_context.method == 'POST':
            content = ''
            data = http_context.json_body()
            if 'admins_print' in data:
                for k, v in self.EMAIL_MAPPING.items():
                    data['admins_print'] = data['admins_print'].replace(k, v)

            def convert_value(v):
                if type(v) is int:
                    return str(v)
                elif type(v) is bool:
                    return '"yes"' if v else '"no"'
                else:
                    return '"%s"' % v

            values_found = []

            for line in open(path):
                originalLine = line
                if line.startswith(('$', '#$')):
                    line = line.strip().lstrip('#$').rstrip(';')
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip()

                    if k in data:
                        newValue = convert_value(data[k])
                        values_found.append(k)

                        originalLine = originalLine.replace(v, newValue)
                        if newValue not in v:
                            originalLine = originalLine.lstrip('#')

                content += originalLine

            for k in data:
                if k not in values_found:
                    content += "$%s=%s;\n" % (k, convert_value(data[k]))

            lm_backup_file(path)
            with open(path, 'w') as f:
                f.write(content)

    @url(r'/api/lm/settings/school-share')
    @authorize('lm:settings')
    @endpoint(api=True)
    def handle_api_school_share(self, http_context):
        path = '/home/share/school'
        if http_context.method == 'GET':
            print os.stat(path).st_mode
            return os.stat(path).st_mode & 0o3777 == 0o3777
        else:
            if http_context.json_body():
                os.chmod(path, 0o3777)
            else:
                os.chmod(path, 0o0700)
