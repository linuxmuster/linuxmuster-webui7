"""
Classes definitions to read, parse and save config files.
"""

import os
import os.path
import logging
import abc
import csv
import magic
import filecmp
import time
import yaml
from configobj import ConfigObj

from .fieldnames import csv_fieldnames


# Allow 1 MiB for csv
csv.field_size_limit(2**20)

ALLOWED_PATHS = [
                # Webui settings
                '/etc/linuxmuster/webui/config.yml',
                # used for school.conf or *.csv in lmn_settings, lmn_devices and lmn_users
                '/etc/linuxmuster/sophomorix/',
                # used in lmn_linbo for start.conf
                '/srv/linbo',
                # used in lmn_settings for subnets configuration
                '/etc/linuxmuster/subnets.csv',
                # used in lmn_settings for holidays configuration
                '/etc/linuxmuster/holidays.yml',
                # used in lmn_settings
                '/var/lib/linuxmuster/setup.ini',
                # user in setup wizard during install
                '/tmp/setup.ini',
                # used in lmn_permissions
                '/usr/lib/linuxmuster-webui/plugins',
                ]

EMPTY_LINE_MARKER = '###EMPTY#LINE'


def convertBool(boolean):
    if type(boolean) is bool:
        return 'yes' if boolean else 'no'
    return boolean


class LMNFile(metaclass=abc.ABCMeta):
    """
    Meta class to handle all type of config file used in linuxmuster's project,
    e.g. ini, csv, linbo config files.
    """

    def __new__(cls, file, mode, delimiter=';', fieldnames=None):
        """
        Parse the extension of the file and choose the right subclass to handle
        the file.

        :param file: File to open
        :type file: string
        :param mode: Read, write, e.g. 'r' or 'wb'
        :type mode: string
        :param delimiter: Useful for CSV files
        :type delimiter: string
        :param fieldnames: Useful for CSV files
        :type fieldnames: list of strings
        """

        # Cannot filter start.conf with extension
        if file.split('/')[-1].startswith('start.conf') and os.path.splitext(file)[-1] != '.vdi':
            obj = object.__new__(StartConfLoader)
            obj.__init__(file, mode, delimiter=delimiter, fieldnames=fieldnames)
            return obj

        ext = os.path.splitext(file)[-1]
        for child in cls.__subclasses__():
            if child.hasExtension(ext):
                obj = object.__new__(child)
                obj.__init__(file, mode, delimiter=delimiter, fieldnames=fieldnames)
                return obj

    def __init__(self, file, mode, delimiter=';', fieldnames=None):
        self.file = file
        self.opened = ''
        self.data = ''
        self.mode  = mode
        self.encoding = self.detect_encoding()
        self.comments = []
        self.check_allowed_path()
        self.delimiter = delimiter

        if self.file.endswith('.csv'):
            # Fieldnames aliases for some common CSV files
            for model in sorted(csv_fieldnames):
                # dict must be sorted, because students is a prefix of extrastudents
                if self.file.startswith('/etc/linuxmuster/') \
                    and self.file.endswith(f'{model}.csv'):
                    self.fieldnames = csv_fieldnames[model]
                    break
            else:
                self.fieldnames = fieldnames

    @classmethod
    def hasExtension(cls, ext):
        """
        Determine if file should be handled here.

        :param ext: Extension of a file, e.g. ini
        :type ext: string
        :return: File handled or not
        :rtype: bool
        """

        if ext in cls.extensions:
            return True
        return False

    @abc.abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def read(self):
        return self.data

    def backup(self):
        """
        Create a backup of a file if in allowed paths, but on ly keeps 10 backups.
        Backup files names scheme is `.<name>.bak.<timestamp>`
        """

        if not os.path.exists(self.file):
            return

        folder, name = os.path.split(self.file)
        backups = sorted([x for x in os.listdir(folder) if x.startswith(f'.{name}.bak.')])
        while len(backups) > 10:
            os.unlink(os.path.join(folder, backups[0]))
            backups.pop(0)

        backup_path = folder + '/.' + name + '.bak.' + str(int(time.time()))
        with open(backup_path, 'w') as f:
            f.write(self.opened.read())

        # Set same permissions as original file
        perms = os.stat(self.file).st_mode
        os.chmod(backup_path, perms)

    # @abc.abstractmethod
    # def __iter__(self):
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def __next__(self):
    #     raise NotImplementedError

    def check_allowed_path(self):
        """
        Check path before modifying files for security reasons.

        :return: File path in allowed paths.
        :rtype: bool
        """

        allowed_path = False
        for rootpath in ALLOWED_PATHS:
            if rootpath in self.file:
                allowed_path = True
                break

        if allowed_path and '..' not in self.file:
            return True
        raise IOError(_("Access refused."))  # skipcq: PYL-E0602

    def detect_encoding(self):
        """
        Try to detect encoding of the file through magic numbers.

        :return: Detected encoding
        :rtype: string
        """

        if not os.path.isfile(self.file):
            #logging.debug(f'Detected encoding for {self.file} : no file, using utf-8')
            return 'utf-8'
        loader = magic.Magic(mime_encoding=True)
        encoding = loader.from_file(self.file)
        if 'ascii' in encoding or encoding == "binary":
            #logging.debug(f'Detected encoding for {self.file} : ascii, but using utf-8')
            return 'utf-8'
        #logging.debug(f'Detected encoding for {self.file} : {encoding}')
        return encoding


class LinboLoader(LMNFile):
    """
    Handler for linbo's cloop informations files.
    """

    extensions = ['.desc', '.reg', '.postsync', '.info', '.macct', '.prestart']

    def __enter__(self):
        self.opened = open(self.file, self.mode, encoding=self.encoding)
        return self.opened

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.opened.close()


class YAMLLoader(LMNFile):
    """
    Handler for yaml files.
    """

    extensions = ['.yml', '.vdi']

    def __enter__(self):
        if os.geteuid() == 0:
            # Creating empty file if it does not exist
            if not os.path.exists(self.file):
                open(self.file, 'w').close()
            os.chmod(self.file, 384)  # 0o600
        self.opened = open(self.file, 'r')
        if 'r' in self.mode or '+' in self.mode:
            self.data = yaml.load(self.opened, Loader=yaml.SafeLoader)
        return self

    def write(self, data):
        tmp = self.file + '_tmp'
        with open(tmp, 'w', encoding=self.encoding) as f:
            f.write(
                yaml.safe_dump(
                    data,
                    default_flow_style=False,
                    encoding='utf-8',
                    allow_unicode=True
                ).decode('utf-8')
            )
        if not filecmp.cmp(tmp, self.file):
            self.backup()
            os.rename(tmp, self.file)
        else:
            os.unlink(tmp)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.opened.close()

class CSVLoader(LMNFile):
    """
    Handler for csv files.
    """

    extensions = ['.csv']

    def __enter__(self):
        self.opened = open(self.file, 'r', encoding=self.encoding)
        if 'r' in self.mode or '+' in self.mode:
            # Removing leading and trailing spaces for all fields
            trim = []
            for line in self.opened:
                trim.append(self.delimiter.join(
                    [field.strip() for field in line.split(self.delimiter)]
                ))
            self.data = csv.DictReader(
                (line if len(line) > 3 else EMPTY_LINE_MARKER for line in trim),
                delimiter = self.delimiter,
                fieldnames = self.fieldnames
            )
        return self

    def read(self):
        return list(self.data)

    def write(self, data):
        tmp = self.file + '_tmp'
        with open(tmp, 'w', encoding=self.encoding) as f:
            writer = csv.DictWriter(
                f,
                delimiter=';',
                fieldnames = self.fieldnames,
                lineterminator = '\n'
            )
            for elt in data:
                first_field = elt[self.fieldnames[0]]
                if first_field in ['', EMPTY_LINE_MARKER]:
                    f.write(first_field.replace(EMPTY_LINE_MARKER, '') + '\n')
                else:
                    writer.writerow(elt)
        if not filecmp.cmp(tmp, self.file):
            self.backup()
            os.rename(tmp, self.file)
        else:
            os.unlink(tmp)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.opened:
            self.opened.close()


class ConfigLoader(LMNFile):
    extensions = ['.ini', '.conf']

    def __enter__(self):
        self.opened = open(self.file, 'r', encoding=self.encoding)
        if 'r' in self.mode or '+' in self.mode:
            self.data = ConfigObj(
                self.file, encoding='utf-8',
                write_empty_values=True,
                stringify=True,
                list_values=False
            )
            for section, options in self.data.items():
                for key, value in options.items():
                    value = int(value) if value.isdigit() else value
                    value = True if value == 'yes' else value
                    value = False if value == 'no' else value
                    self.data[section][key] = value
        return self

    def __exit__(self, *args):
        if self.opened:
            self.opened.close()

    def write(self, data):
        for section, options in data.items():
                for key, value in options.items():
                    value = 'yes' if value is True else value
                    value = 'no' if value is False else value
                    self.data[section][key] = value
        if self.opened.closed:
           self.opened = open(self.file, 'r', encoding=self.encoding)
        self.backup()
        self.opened.close()
        self.data.write()

class StartConfLoader(LMNFile):

    def __enter__(self):
        if os.path.isfile(self.file):
            self.opened = open(self.file, 'r', encoding=self.encoding)
            if 'r' in self.mode or '+' in self.mode:
                self.data = {
                    'config': {},
                    'partitions': [],
                    'os': [],
                }
                for line in self.opened:
                    line = line.split('#')[0].strip()

                    if line.startswith('['):
                        section = {}
                        section_name = line.strip('[]')
                        if section_name == 'Partition':
                            self.data['partitions'].append(section)
                        elif section_name == 'OS':
                            self.data['os'].append(section)
                        else:
                            self.data['config'][section_name] = section
                    elif '=' in line:
                        k, v = line.split('=', 1)
                        v = v.strip()
                        if v in ['yes', 'no']:
                            v = v == 'yes'
                        section[k.strip()] = v
        return self

    def __exit__(self, *args):
        if self.opened:
            self.opened.close()

    def write(self, data):
        content = ''

        for section_name, section in data['config'].items():
            content += f'[{section_name}]\n'
            for k, v in section.items():
                content += f'{k} = {convertBool(v)}\n'
            content += '\n'

        for partition in data['partitions']:
            content += '[Partition]\n'
            for k, v in partition.items():
                if k[0] == '_':
                    continue
                content += f'{k} = {convertBool(v)}\n'
            content += '\n'

        for partition in data['os']:
            content += '[OS]\n'
            for k, v in partition.items():
                content += f'{k} = {convertBool(v)}\n'
            content += '\n'

        tmp = self.file + '_tmp'
        with open(tmp, 'w') as f:
            f.write(content)

        if os.path.isfile(self.file):
            if not filecmp.cmp(tmp, self.file):
                self.backup()
                os.rename(tmp, self.file)
            else:
                os.unlink(tmp)
        else:
            os.rename(tmp, self.file)

        os.chmod(self.file, 0o755)
