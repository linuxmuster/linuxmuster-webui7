import os
import json
import subprocess

from jadi import component
from aj.auth import authorize
from aj.api.http import get, post, delete, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.lmnfile import LMNFile
from aj.plugins.lmn_linbo4.images import LinboImageManager

@component(HttpPlugin)
class Handler(HttpPlugin):
    LINBO_PATH = '/srv/linbo'
    GRUB_PATH = f'{LINBO_PATH}/boot/grub'

    def __init__(self, context):
        self.context = context
        self.mgr = LinboImageManager.get(self.context)

    @get(r'/api/lmn/linbo4/groups')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_list_groups(self, http_context):
        """
        List all start.conf to get linbo groups.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of linbo4 groups
        :rtype: list
        """

        groups = []
        for file in os.listdir(self.LINBO_PATH):
            path = os.path.join(self.LINBO_PATH, file)
            if (
                file.startswith('start.conf.')
                and not file.endswith('.vdi')
                and not os.path.islink(path)
                and os.path.isfile(path)
            ):
                groups.append(file.split(".")[-1])
        return groups

    @get(r'/api/lmn/linbo4/configs')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_configs(self, http_context):
        r = []
        for file in os.listdir(self.LINBO_PATH):
            path = os.path.join(self.LINBO_PATH, file)
            if (
                file.startswith('start.conf.')
                and not file.endswith('.vdi')
                and not os.path.islink(path)
                and os.path.isfile(path)
            ):
                with LMNFile(path, 'r') as f:
                    data = f.read()
                    os_list = data.get('os', [])
                    linbo_settings = data.get('config', {}).get('LINBO', {})

                images = []
                for OS in os_list:
                    image = OS.get('BaseImage', '')
                    if image.endswith('.qcow2') or image.endswith('.cloop'):
                        images.append(image)

                r.append({
                        'file': file,
                        'images': images,
                        'settings': linbo_settings
                })
        return r

    @get(r'/api/lmn/linbo4/examples/(?P<type>.+)')
    @authorize('lm:linbo:examples')
    @endpoint(api=True)
    def handle_api_examples(self, http_context, type):

        valid_extensions = ['reg', 'postsync', 'prestart']

        r = []
        for file in os.listdir(os.path.join(self.LINBO_PATH, 'examples')):
            if type == "config":
                if file.startswith('start.conf.'):
                    r.append(file)
            elif type in valid_extensions:
                if file.endswith(f'.{type}'):
                    r.append(file)
        return r

    @get(r'/api/lmn/linbo4/icons')
    @authorize('lm:linbo:icons')
    @endpoint(api=True)
    def handle_api_icons(self, http_context):
        icons = []
        available_ext = ['.svg']
        for f in os.listdir(os.path.join(self.LINBO_PATH, 'icons')) :
            if f[-4:] in available_ext:
                icons.append(f)
        return icons

    @get(r'/api/lmn/linbo4/icons/(?P<name>.+)')
    @endpoint(api=False, page=True)
    def handle_api_icons_read(self, http_context, name):
        root = '/srv/linbo/icons/'
        path = os.path.abspath(os.path.join(root, name))

        if not path.startswith(root):
            return http_context.respond_forbidden()
        return http_context.file(path, inline=True, name=name.encode())

    
    @get(r'/api/lmn/linbo4/vdi/(?P<name>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_get_vdi_image(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)
        if os.path.exists(path):
            with LMNFile(path, 'r') as settings:
                vdiSettings = settings.read()
        else:
            vdiSettings = None
        return vdiSettings

    @post(r'/api/lmn/linbo4/vdi/(?P<name>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_post_vdi_image(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)
        if os.path.exists(path):
            data = http_context.json_body()
            with open(path, 'w') as settings:
                json.dump(data, settings, indent=4)
            os.chmod(path, 0o755)

    @get(r'/api/lmn/linbo4/config/(?P<name>.+)')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_get_config(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)

        with LMNFile(path, 'r') as f:
            config = f.read()
        return config

    @delete(r'/api/lmn/linbo4/config/(?P<name>.+)')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_delete_config(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)
        group = name.split(".")[-1]
        grub_cfg_path = os.path.join(self.GRUB_PATH, f'{group}.cfg')
        with LMNFile(path, 'r') as f:
            f.backup()
        os.unlink(path)
        if os.path.isfile(grub_cfg_path):
            os.unlink(grub_cfg_path)

    @post(r'/api/lmn/linbo4/config/(?P<name>.+)')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_post_config(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)
        data = http_context.json_body()

        with LMNFile(path, 'w') as f:
            f.write(data)

    @get(r'/lmn/download/linbo.iso')
    @endpoint(page=True)
    def handle_linbo_iso(self, http_context):
        return http_context.file('/srv/linbo/linbo.iso', inline=False, name=b'linbo.iso')

    @get(r'/api/lmn/linbo4/images')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_images(self, http_context):
        # Update list of images
        self.mgr.list()
        return [imageGroup.to_dict()
                for name,imageGroup in self.mgr.linboImageGroups.items()
                ]

    @post(r'/api/lmn/linbo4/images/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_post_image(self, http_context, image=None):
        data = http_context.json_body()['data']
        diff = http_context.json_body()['diff']
        self.mgr.save_extras(image, data, diff=diff)

    @delete(r'/api/lmn/linbo4/images/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_delete_image(self, http_context, image=None):
        self.mgr.delete(image)

    @post(r'/api/lmn/linbo4/renameImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_rename_image(self, http_context, image=None):

        new_name = http_context.json_body()['new_name']
        self.mgr.rename(image, new_name)

    @post(r'/api/lmn/linbo4/duplicateImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_rename_image(self, http_context, image=None):

        new_name = http_context.json_body()['new_name']
        self.mgr.duplicate(image, new_name)

    @post(r'/api/lmn/linbo4/restoreBackupImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_restore_image(self, http_context, image=None):

        date = http_context.json_body()['date']
        self.mgr.restore(image, date)

    @post(r'/api/lmn/linbo4/deleteBackupImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_delete_backup(self, http_context, image=None):

        date = http_context.json_body()['date']
        self.mgr.delete(image, date=date)

    @post(r'/api/lmn/linbo4/saveBackupImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_save_backup(self, http_context, image=None):

        data = http_context.json_body()['data']
        timestamp = http_context.json_body()['timestamp']
        self.mgr.save_extras(image, data, timestamp=timestamp)

    @delete(r'/api/lmn/linbo4/deleteDiffImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_delete_diff(self, http_context, image=None):

        self.mgr.delete(image, diff=True)

    @get(r'/api/lmn/linbo4/restart-services')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_linbo_restart_services(self, http_context):
        """
        Restart the torrent and multicast services.
        Needed if there was some changes on a image.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        try:
            subprocess.check_call(['systemctl', 'restart', 'linbo-multicast.service', 'linbo-torrent.service'])
            return True
        except Exception as e:
            raise EndpointError(None, message=str(e))
