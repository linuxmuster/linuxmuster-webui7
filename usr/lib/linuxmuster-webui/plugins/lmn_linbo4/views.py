import os
import json

from jadi import component
from aj.auth import authorize
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.lmn_common.lmnfile import LMNFile
from aj.plugins.lmn_linbo4.images import LinboImageManager

@component(HttpPlugin)
class Handler(HttpPlugin):
    LINBO_PATH = '/srv/linbo'

    def __init__(self, context):
        self.context = context
        self.mgr = LinboImageManager.get(self.context)

    @url(r'/api/lm/linbo4/configs')
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

    @url(r'/api/lm/linbo4/examples')
    @authorize('lm:linbo:examples')
    @endpoint(api=True)
    def handle_api_examples(self, http_context):
        r = []
        for file in os.listdir(os.path.join(self.LINBO_PATH, 'examples')):
            if file.startswith('start.conf.'):
                r.append(file)
        return r

    @url(r'/api/lm/linbo4/examples-regs')
    @authorize('lm:linbo:examples')
    @endpoint(api=True)
    def handle_api_examples_regs(self, http_context):
        r = []
        for file in os.listdir(os.path.join(self.LINBO_PATH, 'examples')):
            if file.endswith('.reg'):
                r.append(file)
        return r

    @url(r'/api/lm/linbo4/examples-postsyncs')
    @authorize('lm:linbo:examples')
    @endpoint(api=True)
    def handle_api_examples_postsyncs(self, http_context):
        r = []
        for file in os.listdir(os.path.join(self.LINBO_PATH, 'examples')):
            if file.endswith('.postsync'):
                r.append(file)
        return r

    @url(r'/api/lm/linbo4/examples-prestart')
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

    @url(r'/api/lm/linbo4/examples-prestart')
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

    @url(r'/api/lm/linbo4/icons')
    @authorize('lm:linbo:icons')
    @endpoint(api=True)
    def handle_api_icons(self, http_context):
        return os.listdir(os.path.join(self.LINBO_PATH, 'icons'))

    @url(r'/api/lm/linbo4/icons/read/(?P<name>.+)')
    @endpoint(api=False, page=True)
    def handle_api_icons_read(self, http_context, name):
        root = '/srv/linbo/icons/'
        path = os.path.abspath(os.path.join(root, name))

        if not path.startswith(root):
            return http_context.respond_forbidden()
        return http_context.file(path, inline=False, name=name.encode())

    
    @url(r'/api/lm/linbo4/vdi/(?P<name>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_vdi_image(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)
        if http_context.method == 'GET':
            if os.path.exists(path):
                with LMNFile(path, 'r') as settings:
                    vdiSettings = settings.read()

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
                with LMNFile(path, 'w') as settings:
                    settings.write(json.dumps(data, indent=4))
                os.chmod(path, 0o755)

    @url(r'/api/lm/linbo4/config/(?P<name>.+)')
    @authorize('lm:linbo:configs')
    @endpoint(api=True)
    def handle_api_config(self, http_context, name=None):
        path = os.path.join(self.LINBO_PATH, name)

        if http_context.method == 'GET':
            with LMNFile(path, 'r') as f:
                config = f.read()
            return config

        if http_context.method == 'DELETE':
            with LMNFile(path, 'r') as f:
                f.backup()
            os.unlink(path)

        if http_context.method == 'POST':
            data = http_context.json_body()

            with LMNFile(path, 'w') as f:
                f.write(data)

    @url(r'/api/lm/linbo.iso')
    @endpoint(api=False, page=True)
    def handle_linbo_iso(self, http_context):
        return http_context.file('/srv/linbo/linbo.iso', inline=False, name=b'linbo.iso')

    @url(r'/api/lm/linbo4/images')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_images(self, http_context):
        # Update list of images
        self.mgr.list()
        return [imageGroup.to_dict()
                for name,imageGroup in self.mgr.linboImageGroups.items()
                ]

    @url(r'/api/lm/linbo4/image/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_image(self, http_context, image=None):

        if http_context.method == 'POST':
            data = http_context.json_body()
            self.mgr.save_extras(image, data)

        if http_context.method == 'DELETE':
            self.mgr.delete(image)

    @url(r'/api/lm/linbo4/duplicateImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_duplicate_image(self, http_context, image=None):
        pass

    @url(r'/api/lm/linbo4/renameImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_rename_image(self, http_context, image=None):

       if http_context.method == 'POST':
            new_name = http_context.json_body()['new_name']
            self.mgr.rename(image, new_name)

    @url(r'/api/lm/linbo4/restoreBackupImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_restore_image(self, http_context, image=None):

        if http_context.method == 'POST':
            timestamp = http_context.json_body()['timestamp']
            self.mgr.restore(image, timestamp)

    @url(r'/api/lm/linbo4/deleteBackupImage/(?P<image>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_delete_backup(self, http_context, image=None):

        if http_context.method == 'POST':
            timestamp = http_context.json_body()['timestamp']
            self.mgr.delete(image, timestamp)

    @url(r'/api/lm/linbo4/saveBackupImage/(?P<image>.+)/(?P<timestamp>.+)')
    @authorize('lm:linbo:images')
    @endpoint(api=True)
    def handle_api_save_backup(self, http_context, image=None, timestamp=None):
        pass
