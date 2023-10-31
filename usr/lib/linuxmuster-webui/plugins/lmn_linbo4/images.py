import os
import shutil
import subprocess
import logging
from datetime import datetime

from jadi import service
from aj.plugins.lmn_common.lmnfile import LMNFile
from aj.api.endpoint import EndpointError


LINBO_PATH = '/srv/linbo/images'
TIMESTAMP_FMT = '%Y%m%d%H%M'
DATE_UI_FMT = '%d/%m/%Y %H:%M'


# Filenames like ubuntu.qcow2.desc
EXTRA_IMAGE_FILES = ['desc', 'info',  'vdi']
EXTRA_NONEDITABLE_IMAGE_FILES = ['torrent', 'macct']

# Filenames like ubuntu.reg
EXTRA_COMMON_FILES = ['reg', 'postsync', 'prestart']

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
DIFF_IMAGE = "qdiff"

def date2timestamp(date):
    return datetime.strptime(date, DATE_UI_FMT).strftime(TIMESTAMP_FMT)

def timestamp2date(timestamp):
    return datetime.strptime(timestamp, TIMESTAMP_FMT).strftime(DATE_UI_FMT)

class LinboImage:
    """
    A class to manage a linbo image or a backup image
    """

    def __init__(self, name, backup=False, timestamp=None, diff=False):
        self.name = name
        self.backup = backup
        self.diff = diff
        self.timestamp = timestamp
        self.load_info()

    def _torrent_stop(self):
        try:
            subprocess.check_output(['/usr/sbin/linbo-torrent', 'stop', os.path.join(self.path, f'{self.image}.torrent')])
        except Exception as e:
            logging.error(f'Unable to stop torrent service for {self.image} : {e.output}')

    def load_info(self):
        """
        Prepare all variables to manage the image object ( path, name, extra files )
        """

        if self.diff:
            self.image = f"{self.name}.{DIFF_IMAGE}"
        else:
            self.image = f"{self.name}.{IMAGE}"

        if self.backup:
            self.path = os.path.join(LINBO_PATH, self.name, 'backups', self.timestamp)
            self.date = timestamp2date(self.timestamp)
        else:
            self.path = os.path.join(LINBO_PATH, self.name)
            self.timestamp = self.get_timestamp()
            self.date = timestamp2date(self.timestamp)

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
                if extra == 'desc' and os.getuid() == 0:
                    with LMNFile(extra_file, 'w') as f:
                        pass
                    os.chmod(extra_file, EXTRA_PERMISSIONS_MAPPING[extra])

        for extra in EXTRA_COMMON_FILES:
            if self.diff and extra == 'postsync':
                continue
            extra_file = os.path.join(self.path, f"{self.name}.{extra}")
            if os.path.isfile(extra_file):
                with LMNFile(extra_file, 'r') as f:
                    self.extras[extra] = f.read()
            else:
                self.extras[extra] = None

    def get_timestamp(self):
        info_path = os.path.join(self.path, f"{self.image}.info")
        if os.path.isfile(info_path):
            with open(info_path, 'r') as info:
                for line in info:
                    if 'timestamp' in line:
                        # Support timestamp=2021..
                        # and timestamp="2021..."
                        return line.strip().split('=')[1].strip('"')
        logging.warning(f"Can not find timestamp for {self.image}, using current time as timestamp !")
        return datetime.now().strftime(TIMESTAMP_FMT)

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

        for extra in EXTRA_COMMON_FILES:
            if self.diff and extra == 'postsync':
                continue
            path = os.path.join(self.path, f"{self.name}.{extra}")
            if os.path.exists(path):
                os.unlink(path)

    def delete(self):
        """
        Completely remove an image and its directory.
        """

        if not self.backup:
            self._torrent_stop()

        self.delete_files()

        if not self.diff:
            # Remove directory
            try:
                os.rmdir(self.path)
            except OSError as e:
                raise EndpointError(e)

    def rename(self, new_name):
        """
        Rename a LinboImage and all its files.
        """

        if self.diff:
            new_image_name = f"{new_name}.{DIFF_IMAGE}"
        else:
            new_image_name = f"{new_name}.{IMAGE}"

        if not self.backup:
            self._torrent_stop()

        # Rename image
        os.rename(os.path.join(self.path, self.image),
                  os.path.join(self.path, new_image_name))

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

                    continue

                os.rename(actual, os.path.join(self.path, f"{new_image_name}.{extra}"))

        for extra in EXTRA_COMMON_FILES:
            actual = os.path.join(self.path, f"{self.name}.{extra}")
            if os.path.exists(actual):
                os.rename(actual, os.path.join(self.path, f"{new_name}.{extra}"))

        # Move directory
        if not self.backup and not self.diff:
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
            extra_content = data.get(extra, '')
            if extra_content or (extra == "desc" and extra_content is not None):
                with LMNFile(path, 'w') as f:
                    f.write(data[extra])
                os.chmod(path, EXTRA_PERMISSIONS_MAPPING[extra])
            else:
                if os.path.exists(path):
                    os.unlink(path)

        for extra in EXTRA_COMMON_FILES:
            path = os.path.join(self.path, f"{self.name}.{extra}")
            extra_content = data.get(extra, '')
            if extra_content:
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
            'postsync': self.extras.get('postsync', ''),
            'vdi': self.extras['vdi'],
            'prestart': self.extras['prestart'],
            'backup': self.backup,
            'diff': self.diff,
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
        self.get_diff()

    def get_backups(self):
        """
        Browse current tree to find all backups image.
        """

        if os.path.exists(self.backup_path):
            for timestamp in os.listdir(self.backup_path):
                try:
                    # Is it a valid timestamp ?
                    timestamp2date(timestamp)
                except ValueError:
                    # Not a backup done with Linbo, passing
                    continue
                for file in os.listdir(os.path.join(self.backup_path, timestamp)):
                    if file.endswith(f".{IMAGE}"):
                        self.backups[timestamp2date(timestamp)] = LinboImage(
                            self.name,
                            backup=True,
                            timestamp=timestamp
                        )

    def get_diff(self):
        """
        Browse current tree to find a differential image.
        """

        if os.path.exists(os.path.join(LINBO_PATH, self.name, f'{self.name}.{DIFF_IMAGE}')):
            self.diff_image = LinboImage(self.name, diff=True)
        else:
            self.diff_image = None

    def rename(self, new_name):
        """
        Rename an image and all his backups.
        """

        for timestamp, backup in self.backups.items():
            backup.rename(new_name)

        if self.diff_image:
            self.diff_image.rename(new_name)

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
        Delete basic image, all backups, diff image and all config files.
        """

        for timestamp, backup in self.backups.items():
            backup.delete()

        if self.diff_image:
            self.diff_image.delete()

        if os.path.isdir(self.backup_path):
            try:
                os.rmdir(self.backup_path)
            except OSError as e:
                raise EndpointError(e)

        self.base.delete()

    def to_dict(self):
        result = self.base.to_dict()
        result['diff_image'] = self.diff_image.to_dict() if self.diff_image else {}
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
                    if file == f'{dir}.{IMAGE}':
                        self.linboImageGroups[dir] = LinboImageGroup(dir)

    def delete(self, group, date=0, diff=False):
        """
        Delete a whole image and its backups. If date is given, only delete an
        associated backup. date and diff parameter excludes each other.

        :param group: Name of the linbo image
        :type group: str
        :param date: timestamp of a backup
        :type date: str
        :param diff: only delete a differential image
        :type diff: bool
        """

        if group in self.linboImageGroups:
            if diff:
                # Only delete a differential image
                self.linboImageGroups[group].diff_image.delete()
            elif date in self.linboImageGroups[group].backups:
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

    def duplicate(self, group, new_name):
        """
        Duplicate a whole linbo image without backups.

        :param group: Name of the linbo image to duplicate
        :type group: str
        :param new_name: New name for the linbo image
        :type new_name: str
        """

        if os.path.isdir(os.path.join(LINBO_PATH, new_name)):
            raise EndpointError(f"Directory {new_name} already exists")

        if group in self.linboImageGroups:
            shutil.copytree(
                os.path.join(LINBO_PATH, group),
                os.path.join(LINBO_PATH, new_name),
                ignore=lambda x,y: 'backups'
            )

            old_prefix = f'{group}.'
            new_prefix = f'{new_name}.'

            for file in os.listdir(os.path.join(LINBO_PATH, new_name)):
                if file.startswith(old_prefix):
                    os.rename(
                       os.path.join(LINBO_PATH, new_name, file),
                       os.path.join(LINBO_PATH, new_name, file.replace(old_prefix, new_prefix)),
                    )


            self.linboImageGroups[new_name] = LinboImageGroup(new_name)
            self.linboImageGroups[new_name].rename(new_name)

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
                timestamp = datetime.now().strftime(TIMESTAMP_FMT)

                new_backup_dir = os.path.join(
                    imageGroup.base.path,
                    'backups',
                    timestamp
                )

                if os.path.isdir(new_backup_dir):
                    raise EndpointError(f"Backup directory {new_backup_dir} already exists")

                os.mkdir(new_backup_dir)

                # Move base image to backup/timestamp
                for file in os.listdir(imageGroup.base.path):
                    # Avoid copying backups dir in itself
                    if os.path.isfile(os.path.join(imageGroup.base.path, file)):
                        shutil.move(os.path.join(imageGroup.base.path, file),
                                new_backup_dir)

                # Move backup to base image
                for file in os.listdir(imageGroup.backups[date].path):
                    shutil.move(os.path.join(imageGroup.backups[date].path, file),
                                imageGroup.base.path)

                # Cleanup and reload
                imageGroup.backups[date].delete()
                self.linboImageGroups[group].load()

    def save_extras(self, group, data, timestamp=None, diff=False):
        """
        Save extra files for a base image, a backup or a differential
        image. timestamp and diff parameters excludes each other.

        :param group: Name of the linbo image
        :type group: str
        :param data: Content of the extra files
        :type data: dict
        :param timestamp: timestamp of a backup
        :type timestamp: str
        :param diff: data onlyc concern a diff image
        :type diff: bool
        """

        if timestamp:
            date = timestamp2date(timestamp)
        else:
            date = 0
        if group in self.linboImageGroups:
            imageGroup = self.linboImageGroups[group]
            if diff:
                imageGroup.diff_image.save_extras(data)
            elif date in imageGroup.backups:
                imageGroup.backups[date].save_extras(data)
            else:
                imageGroup.base.save_extras(data)