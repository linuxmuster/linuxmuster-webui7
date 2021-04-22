import os
import json

from jadi import component
from aj.auth import authorize
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.lmn_common.api import lmn_backup_file, lmn_write_configfile
from aj.plugins.lmn_common.lmnfile import LMNFile
from aj.plugins.lmn_common.api import LinuxmusterConfig

@component(HttpPlugin)
class Handler(HttpPlugin):
    LINBO_PATH = '/srv/linbo'

    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/linbo/configs')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_configs(self, http_context):
        r = []
        for file in os.listdir(self.LINBO_PATH):
            if file.startswith('start.conf.'):
                if not file.endswith('.vdi'):
                    if not os.path.islink(os.path.join(self.LINBO_PATH, file)):
                        r.append(file)
        return r

    @url(r'/api/lm/linbo/examples')
    @authorize('lm:linbo:examples')
    @endpoint(api=True)
    def handle_api_examples(self, http_context):
        r = []
        for file in os.listdir(os.path.join(self.LINBO_PATH, 'examples')):
            if file.startswith('start.conf.'):
                r.append(file)
        return r

    @url(r'/api/lm/linbo/examples-regs')
    @authorize('lm:linbo:examples')
    @endpoint(api=True)
    def handle_api_examples_regs(self, http_context):
        r = []
        for file in os.listdir(os.path.join(self.LINBO_PATH, 'examples')):
            if file.endswith('.reg'):
                r.append(file)
        return r

    @url(r'/api/lm/linbo/examples-postsyncs')
    @authorize('lm:linbo:examples')
    @endpoint(api=True)
    def handle_api_examples_postsyncs(self, http_context):
        r = []
        for file in os.listdir(os.path.join(self.LINBO_PATH, 'examples')):
            if file.endswith('.postsync'):
                r.append(file)
        return r

    @url(r'/api/lm/linbo/examples-prestart')
    @authorize('lm:linbo:examples')
    @endpoint(api=True)
    def handle_api_examples_prestart(self, http_context):
        """
        List all prestart examples files.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of postsync examples files
        :rtype: list
        """

        r = []
        for file in os.listdir(os.path.join(self.LINBO_PATH, 'examples')):
            if file.endswith('.prestart'):
                r.append(file)
        return r

    @url(r'/api/lm/linbo/icons')
    @authorize('lm:linbo:icons')
    @endpoint(api=True)
    def handle_api_icons(self, http_context):
        return os.listdir(os.path.join(self.LINBO_PATH, 'icons'))

    @url(r'/api/lm/linbo/images')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_images(self, http_context):
        r = []
        for file in os.listdir(self.LINBO_PATH):
            if file.endswith(('.cloop', '.rsync')):
                extra_dict = {}
                for extra in ['desc', 'reg', 'postsync', 'info', 'macct','vdi']:
                    extra_file = os.path.join(self.LINBO_PATH, file + '.' + extra)
                    if os.path.isfile(extra_file):
                        with LMNFile(extra_file, 'r') as f:
                            extra_dict[extra] = f.read()
                    else:
                        extra_dict[extra] = None

                # New convention name without cloop
                prestart_file = os.path.join(self.LINBO_PATH, file[:-6] + '.prestart')
                if os.path.isfile(prestart_file):
                    with LMNFile(prestart_file, 'r') as f:
                        extra_dict['prestart'] = f.read()
                else:
                    extra_dict['prestart'] = None

                r.append({
                    'name': file,
                    'cloop': file.endswith('.cloop'),
                    'rsync': file.endswith('.rsync'),
                    'size': os.stat(os.path.join(self.LINBO_PATH, file)).st_size,
                    'description': extra_dict['desc'],
                    'info': extra_dict['info'],
                    'macct': extra_dict['macct'],
                    'reg': extra_dict['reg'],
                    'postsync': extra_dict['postsync'],
                    'vdi': extra_dict['vdi'],
                    'prestart': extra_dict['prestart'],
                })
        return r

    @url(r'/api/lm/linbo/icons/read/(?P<name>.+)')
    @endpoint(api=False, page=True)
    def handle_api_icons_read(self, http_context, name):
        root = '/srv/linbo/icons/'
        path = os.path.abspath(os.path.join(root, name))

        if not path.startswith(root):
            return http_context.respond_forbidden()
        return http_context.file(path, inline=False, name=name.encode())

    
    @url(r'/api/lm/linbo/vdi/(?P<name>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_vdi_image(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)
        if http_context.method == 'GET':
            if os.path.exists(path):
                settings = LinuxmusterConfig(path)
                settings.load()
                vdiSettings=settings.data
                vdiSettings["cores"] = int(vdiSettings["cores"])
                vdiSettings["memory"] = int(vdiSettings["memory"])
                vdiSettings["tag"] = int(vdiSettings["tag"])
                vdiSettings["minimum_vms"] = int(vdiSettings["minimum_vms"])
                vdiSettings["maxmimum_vms"] = int(vdiSettings["maxmimum_vms"])
                vdiSettings["prestarted_vms"] = int(vdiSettings["prestarted_vms"])
                vdiSettings["timeout_building_master"] = int(vdiSettings["timeout_building_master"])
                vdiSettings["timeout_building_clone"] = int(vdiSettings["timeout_building_clone"])
            else:
                vdiSettings = None
            return vdiSettings
        
        if http_context.method == 'POST':
            if os.path.exists(path):
                data = http_context.json_body()
                lmn_write_configfile(path, json.dumps(data, indent=4))
                os.chmod(path, 0o755)

    @url(r'/api/lm/linbo/image/(?P<name>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_image(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)
        desc_file = path + '.desc'
        info_file = path + '.info'
        macct_file = path + '.macct'
        reg_file = path + '.reg'
        postsync_file = path + '.postsync'

        # New generation names without .cloop
        prestart_file = path[:-6] + '.prestart'

        if http_context.method == 'POST':
            data = http_context.json_body()
            if 'description' in data:
                if data['description']:
                    with LMNFile(desc_file, 'w') as f:
                        f.write(data['description'])
                    os.chmod(desc_file, 0o664)
                else:
                    if os.path.exists(desc_file):
                        os.unlink(desc_file)
            if 'info' in data:
                if data['info']:
                    with LMNFile(info_file, 'w') as f:
                        f.write(data['info'])
                    os.chmod(info_file, 0o664)
                else:
                    if os.path.exists(info_file):
                        os.unlink(info_file)
            if 'macct' in data:
                if data['macct']:
                    with LMNFile(macct_file, 'w') as f:
                        f.write(data['macct'])
                    os.chmod(macct_file, 0o600)
                else:
                    if os.path.exists(macct_file):
                        os.unlink(macct_file)
            if 'reg' in data:
                if data['reg']:
                    with LMNFile(reg_file, 'w') as f:
                        f.write(data['reg'])
                    os.chmod(reg_file, 0o664)
                else:
                    if os.path.exists(reg_file):
                        os.unlink(reg_file)
            if 'postsync' in data:
                if data['postsync']:
                    with LMNFile(postsync_file, 'w') as f:
                        f.write(data['postsync'])
                    os.chmod(postsync_file, 0o664)
                else:
                    if os.path.exists(postsync_file):
                        os.unlink(postsync_file)
            if 'prestart' in data:
                if data['prestart']:
                    with LMNFile(prestart_file, 'w') as f:
                        f.write(data['prestart'])
                    os.chmod(postsync_file, 0o664)
                else:
                    if os.path.exists(postsync_file):
                        os.unlink(postsync_file)
        else:
            for p in [path, desc_file, info_file, macct_file, reg_file, postsync_file]:
                if os.path.exists(p):
                    os.unlink(p)

    @url(r'/api/lm/linbo/config/(?P<name>.+)')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_config(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)

        if http_context.method == 'GET':
            config = {
                'config': {},
                'partitions': [],
                'os': [],
            }
            for line in open(path, 'rb'):
                line = line.decode('utf-8', errors='ignore')
                line = line.split('#')[0].strip()

                if line.startswith('['):
                    section = {}
                    section_name = line.strip('[]')
                    if section_name == 'Partition':
                        config['partitions'].append(section)
                    elif section_name == 'OS':
                        config['os'].append(section)
                    else:
                        config['config'][section_name] = section
                elif '=' in line:
                    k, v = line.split('=', 1)
                    v = v.strip()
                    if v in ['yes', 'no']:
                        v = v == 'yes'
                    section[k.strip()] = v
            return config

        if http_context.method == 'DELETE':
            lmn_backup_file(path)
            os.unlink(path)

        if http_context.method == 'POST':
            content = ''
            data = http_context.json_body()

            def convert(v):
                if type(v) is bool:
                    return 'yes' if v else 'no'
                return v

            for section_name, section in data['config'].items():
                content += '[%s]\n' % section_name
                for k, v in section.items():
                    content += '%s = %s\n' % (k, convert(v))
                content += '\n'
            for partition in data['partitions']:
                content += '[Partition]\n'
                for k, v in partition.items():
                    if k[0] == '_':
                        continue
                    content += '%s = %s\n' % (k, convert(v))
                content += '\n'
            for partition in data['os']:
                content += '[OS]\n'
                for k, v in partition.items():
                    content += '%s = %s\n' % (k, convert(v))
                content += '\n'

            lmn_write_configfile(path, content)
            os.chmod(path, 0o755)

    @url(r'/api/lm/linbo.iso')
    @endpoint(api=False, page=True)
    def handle_linbo_iso(self, http_context):
        return http_context.file('/srv/linbo/linbo.iso', inline=False, name=b'linbo.iso')
