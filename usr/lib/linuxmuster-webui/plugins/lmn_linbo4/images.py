import os
import shutil
import subprocess
import logging
from datetime import datetime

from jadi import service
from aj.plugins.lmn_common.lmnfile import LMNFile

LINBO_PATH = '/srv/linbo/images'

# Filenames like ubuntu.qcow2.desc
EXTRA_IMAGE_FILES = ['desc', 'info',  'vdi']
EXTRA_NONEDITABLE_IMAGE_FILES = ['torrent']

# Filenames like ubuntu.reg
EXTRA_COMMON_FILES = ['reg', 'postsync', 'prestart']
EXTRA_NONEDITABLE_COMMON_FILES = ['macct']

EXTRA_PERMISSIONS_MAPPING = {
    'desc': 0o664,
    'info': 0o664,
    'macct': 0o600,
    'vdi': 0o664,
    'reg': 0o664,
    'postsync': 0o664,
    'prestart': 0o664,
}
IMAGE = "qcow2"

def date2timestamp(date):
    return datetime.strptime(date, '%d/%m/%Y %H:%M').strftime('%Y%m%d%H%M')

def timestamp2date(timestamp):
    return datetime.strptime(timestamp, '%Y%m%d%H%M').strftime('%d/%m/%Y %H:%M')

class LinboImage:
    """
    A class to manage a linbo image or a backup image
    """

    def __init__(self, name, backup=False, timestamp=None):
        self.name = name
        self.backup = backup
        self.timestamp = timestamp
        self.load_info()

    def _torrent_stop(self):
        try:
            subprocess.check_call(['/usr/sbin/linbo-torrent', 'stop', f'{self.image}.torrent'])
        except Exception as e:
            logging.error(f'Unable to stop torrent service for {self.image} : {e}')

    def _torrent_create(self, image=None):
        if not image:
            image = self.image
        try:
            subprocess.check_call(['/usr/sbin/linbo-torrent', 'create', image])
        except Exception as e:
            logging.error(f'Unable to create torrent file for {image} : {e}')

    def load_info(self):
        """
        Prepare all variables to manage the image object ( path, name, extra files )
        """

        self.image = f"{self.name}.{IMAGE}"

        if self.backup:
            self.path = os.path.join(LINBO_PATH, self.name, 'backups', self.timestamp)
            self.date = timestamp2date(self.timestamp)
        else:
            self.path = os.path.join(LINBO_PATH, self.name)
            self.date = None

        self.size = os.stat(os.path.join(self.path, self.image)).st_size
        self.extras = {}
        self.get_extra()

    def get_extra(self):
        """
        Load extra editables config files for the image.
        """

        for extra in EXTRA_IMAGE_FILES:
            extra_file = os.path.join(self.path, f"{self.image}.{extra}")
            if os.path.isfile(extra_file):
                with LMNFile(extra_file, 'r') as f:
                    self.extras[extra] = f.read()
            else:
                self.extras[extra] = None
                # Create empty desc in any case
                if extra == 'desc':
                    with LMNFile(extra_file, 'w') as f:
                        pass
                    os.chmod(extra_file, EXTRA_PERMISSIONS_MAPPING[extra])


        for extra in EXTRA_COMMON_FILES:
            extra_file = os.path.join(self.path, f"{self.name}.{extra}")
            if os.path.isfile(extra_file):
                with LMNFile(extra_file, 'r') as f:
                    self.extras[extra] = f.read()
            else:
                self.extras[extra] = None

    def delete_files(self):
        """
        Delete all files from a LinboImage.
        """

        # Remove image
        image_path = os.path.join(self.path, self.image)
        if os.path.exists(image_path):
            os.unlink(os.path.join(self.path, self.image))

        # Remove extra files
        for extra in EXTRA_IMAGE_FILES + EXTRA_NONEDITABLE_IMAGE_FILES:
            path = os.path.join(self.path, f"{self.image}.{extra}")
            if os.path.exists(path):
                os.unlink(path)

        for extra in EXTRA_COMMON_FILES + EXTRA_NONEDITABLE_COMMON_FILES:
            path = os.path.join(self.path, f"{self.name}.{extra}")
            if os.path.exists(path):
                os.unlink(path)

    def delete(self):
        """
        Completely remove an image an its directory.
        """

        self.delete_files()
        self._torrent_stop()

        # Remove directory
        os.rmdir(self.path)

    def rename(self, new_name):
        """
        Rename a LinboImage and all its files.
        """

        new_image_name = f"{new_name}.{IMAGE}"

        # Rename image
        os.rename(os.path.join(self.path, self.image),
                  os.path.join(self.path, new_image_name))

        self._torrent_stop()

        # Rename extra files
        for extra in EXTRA_IMAGE_FILES + EXTRA_NONEDITABLE_IMAGE_FILES:
            actual = os.path.join(self.path, f"{self.image}.{extra}")
            if os.path.exists(actual):
                # Replace image name in .info file
                if extra == "info":
                    with LMNFile(actual, 'r') as info:
                        data = info.read().replace(self.image, new_image_name)
                    with LMNFile(actual, 'w') as info:
                        info.write(data)

                # Need to generate a new torrent file
                if extra == "torrent":
                    os.unlink(actual)
                    self._torrent_create(new_image_name)
                    continue

                os.rename(actual, os.path.join(self.path, f"{new_image_name}.{extra}"))

        for extra in EXTRA_COMMON_FILES + EXTRA_NONEDITABLE_COMMON_FILES:
            actual = os.path.join(self.path, f"{self.name}.{extra}")
            if os.path.exists(actual):
                os.rename(actual, os.path.join(self.path, f"{new_name}.{extra}"))

        # Move directory
        if not self.backup:
            os.rename(self.path, os.path.join(LINBO_PATH, new_name))

        # Refresh informations
        self.name = new_name

    def save_extras(self, data):
        """
        Save all extra files content.

        :param data: Data to save
        :type data: dict
        """

        for extra in EXTRA_IMAGE_FILES:
            path = os.path.join(self.path, f"{self.image}.{extra}")
            if extra in data and ( data[extra] or extra == 'desc' ):
                with LMNFile(path, 'w') as f:
                    f.write(data[extra])
                os.chmod(path, EXTRA_PERMISSIONS_MAPPING[extra])
            else:
                if os.path.exists(path):
                    os.unlink(path)

        for extra in EXTRA_COMMON_FILES:
            path = os.path.join(self.path, f"{self.name}.{extra}")
            if extra in data and data[extra]:
                with LMNFile(path, 'w') as f:
                    f.write(data[extra])
                os.chmod(path, EXTRA_PERMISSIONS_MAPPING[extra])
            else:
                if os.path.exists(path):
                    os.unlink(path)

    def to_dict(self):
        """
        Convert all necessary infos into a dict for angular.
        """

        return {
            'name': self.name,
            'size': self.size,
            'desc': self.extras['desc'],
            'info': self.extras['info'],
            'reg': self.extras['reg'],
            'postsync': self.extras['postsync'],
            'vdi': self.extras['vdi'],
            'prestart': self.extras['prestart'],
            'backup': self.backup,
            'timestamp': self.timestamp,
            'date': self.date,
        }

class LinboImageGroup:
    """
    Class to handle a basic LinboImage and all his backups.
    """

    def __init__(self, name):
        self.name = name
        self.path = os.path.join(LINBO_PATH, self.name)
        self.backup_path = os.path.join(LINBO_PATH, self.name, 'backups')
        self.load()

    def load(self):
        self.backups = {}
        self.base = LinboImage(self.name)
        self.get_backups()

    def get_backups(self):
        """
        Browse current tree to find all backups image.
        """

        if os.path.exists(self.backup_path):
            for timestamp in os.listdir(self.backup_path):
                for file in os.listdir(os.path.join(self.backup_path, timestamp)):
                    if file.endswith(f".{IMAGE}"):
                        self.backups[timestamp2date(timestamp)] = LinboImage(
                            self.name,
                            backup=True,
                            timestamp=timestamp
                        )

    def rename(self, new_name):
        """
        Rename an image and all his backups.
        """

        for timestamp, backup in self.backups.items():
            backup.rename(new_name)

        self.base.rename(new_name)

        # Refresh informations
        self.base.load_info()

        for timestamp, backup in self.backups.items():
            backup.load_info()

        self.name = new_name
        self.path = os.path.join(LINBO_PATH, self.name)
        self.backup_path = os.path.join(LINBO_PATH, self.name, 'backups')

    def delete(self):
        """
        Delete basic image, all backups and all config files.
        """

        for timestamp, backup in self.backups.items():
            backup.delete()

        if os.path.isdir(self.backup_path):
            os.rmdir(self.backup_path)

        self.base.delete()

    def to_dict(self):
        result = self.base.to_dict()
        result['backups'] = {
            timestamp: backup.to_dict()
            for timestamp, backup in self.backups.items()
        }
        result['selected'] = False
        return result

@service
class LinboImageManager:
    """
    Manager for all Linbo Images.
    """


    def __init__(self, context):
        self.list()

    def list(self):
        """
        Browse LINBO_PATH to discover all linbo images.
        """

        self.linboImageGroups = {}
        if not os.path.isdir(LINBO_PATH):
            return
        for dir in os.listdir(LINBO_PATH):
            if os.path.isdir(os.path.join(LINBO_PATH, dir)):
                for file in os.listdir(os.path.join(LINBO_PATH, dir)):
                    if file.endswith((f'.{IMAGE}')):
                        self.linboImageGroups[dir] = LinboImageGroup(dir)

    def delete(self, group, date=0):
        """
        Delete a whole image and its backups. If date is given, only delete an
        associated backup.

        :param group: Name of the linbo image
        :type group: str
        :param date: timestamp of a backup
        :type date: str
        """

        if group in self.linboImageGroups:
            if date in self.linboImageGroups[group].backups:
                # The object to delete is only a backup
                self.linboImageGroups[group].backups[date].delete()
                self.linboImageGroups[group].load()
            else:
                # Then delete the whole group
                self.linboImageGroups[group].delete()
                del self.linboImageGroups[group]

    def rename(self, group, new_name):
        """
        Rename a whole linbo image and its backups recursiverly.

        :param group: Name of the linbo image
        :type group: str
        :param new_name: New name for the linbo image
        :type new_name: str
        """

        if group in self.linboImageGroups:
            self.linboImageGroups[group].rename(new_name)
            self.linboImageGroups[new_name] = LinboImageGroup(new_name)
            del self.linboImageGroups[group]

    def restore(self, group, date):
        """
        Delete a basic linbo image and restore a backup.

        :param group: Name of the linbo image
        :type group: str
        :param date: timestamp of a backup
        :type date: str
        """

        if group in self.linboImageGroups:
            imageGroup = self.linboImageGroups[group]
            if date in imageGroup.backups:
                imageGroup.base.delete_files()
                for file in os.listdir(imageGroup.backups[date].path):
                    shutil.move(os.path.join(imageGroup.backups[date].path, file),
                                imageGroup.base.path)
                imageGroup.backups[date].delete()
                self.linboImageGroups[group].load()
                imageGroup.base._torrent_create()

    def save_extras(self, group, data, timestamp=None):
        """

        :param group: Name of the linbo image
        :type group: str
        :param data: Content of the extra files
        :type data: dict
        :param timestamp: timestamp of a backup
        :type timestamp: str
        """

        if timestamp:
            date = timestamp2date(timestamp)
        else:
            date = 0
        if group in self.linboImageGroups:
            imageGroup = self.linboImageGroups[group]
            if date in imageGroup.backups:
                imageGroup.backups[date].save_extras(data)
            else:
                imageGroup.base.save_extras(data)

