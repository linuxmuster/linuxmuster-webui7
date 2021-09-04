import os

from aj.plugins.lmn_common.lmnfile import LMNFile

class LinboImage:
    LINBO_PATH = '/srv/linbo/images'
    EXTRA_FILES = ['desc', 'reg', 'postsync', 'info', 'macct', 'vdi']

    def __init__(self, name, backup=False, timestamp=None):
        self.name = name
        self.backup = backup
        self.timestamp = timestamp
        self.load_info()

    def load_info(self):
        self.image = self.name + ".qcow2"

        if self.backup:
            self.path = os.path.join(self.LINBO_PATH, self.name, 'backups', self.timestamp)
        else:
            self.path = os.path.join(self.LINBO_PATH, self.name)

        self.size = os.stat(os.path.join(self.path, self.image)).st_size
        self.extras = {}
        self.get_extra()

    def get_extra(self):
        """
        Search extra config files for the image.

        :return:
        :rtype:
        """

        for extra in self.EXTRA_FILES:
            extra_file = os.path.join(self.path, self.image + '.' + extra)
            if os.path.isfile(extra_file):
                with LMNFile(extra_file, 'r') as f:
                    self.extras[extra] = f.read()
            else:
                self.extras[extra] = None

        prestart_file = os.path.join(self.path, self.name + '.prestart')
        if os.path.isfile(prestart_file):
            with LMNFile(prestart_file, 'r') as f:
                self.extras['prestart'] = f.read()
        else:
            self.extras['prestart'] = None

    def delete(self):
        """
        Delete all files from a LinboImage.

        :return:
        :rtype:
        """

        # Remove image
        os.unlink(os.path.join(self.path, self.image))

        # Remove extra files
        for extra in self.EXTRA_FILES:
            path = os.path.join(self.path, self.image + "." + extra)
            if os.path.exists(path):
                os.unlink(path)

        prestart = os.path.join(self.path, self.name + '.prestart')
        if os.path.exists(prestart):
            os.unlink(prestart)

        # Remove directory
        os.unlink(self.path)

    def rename(self, new_name):
        """
        Rename a LinboImage.

        :return:
        :rtype:
        """

        new_image_name = new_name + ".qcow2"

        # Rename image
        os.rename(os.path.join(self.path, self.image),
                  os.path.join(self.path, new_image_name))

        # Rename extra files
        for extra in ['.desc', '.reg', '.postsync', '.info', '.macct', '.vdi']:
            actual = os.path.join(self.path, self.image + extra)
            if os.path.exists(actual):
                os.rename(actual, os.path.join(self.path, new_image_name + extra))

        prestart =os.path.join(self.path, self.name + '.prestart')
        if os.path.exists(prestart):
            os.rename(prestart, os.path.join(self.path, new_name + '.prestart'))

        # Move directory
        if not self.backup:
            os.rename(self.path, os.path.join(self.LINBO_PATH, new_name))

        # Refresh informations
        self.name = new_name
        self.load_info()

    def to_dict(self):
        return {
            'name': self.name,
            'size': self.size,
            'description': self.extras['desc'],
            'info': self.extras['info'],
            'macct': self.extras['macct'],
            'reg': self.extras['reg'],
            'postsync': self.extras['postsync'],
            'vdi': self.extras['vdi'],
            'prestart': self.extras['prestart'],
        }

class LinboGroupImage:
    LINBO_PATH = '/srv/linbo/images'

    def __init__(self, name):
        self.name = name
        self.path = os.path.join(self.LINBO_PATH, self.name)
        self.backup_path = os.path.join(self.LINBO_PATH, self.name, 'backups')
        self.backups = {}
        self.base = LinboImage(self.name)
        self.get_backups()

    def get_backups(self):
        """

        :return:
        :rtype:
        """

        if os.path.exists(self.backup_path):
            for timestamp in os.listdir(self.backup_path):
                for file in os.listdir(os.path.join(self.backup_path, timestamp)):
                    if file.endswith(".qcow2"):
                        self.backups[timestamp] = LinboImage(
                            self.name,
                            backup=True,
                            timestamp=timestamp
                        )

    def rename(self, new_name):
        """
        Rename an image and all his backups.

        :return:
        :rtype:
        """

        for timestamp, backup in self.backups.items():
            backup.rename(new_name)

        self.base.rename(new_name)
        self.name = new_name
        self.path = os.path.join(self.LINBO_PATH, self.name)


    def to_dict(self):
        result = self.base.to_dict()
        result['backups'] = {
            timestamp: backup.to_dict()
            for timestamp, backup in self.backups.items()
        }
        return result

class LinboImageManager:
    pass