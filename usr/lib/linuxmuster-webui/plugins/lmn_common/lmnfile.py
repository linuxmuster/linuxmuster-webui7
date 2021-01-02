"""
Classes definitions to read, parse and save config files.
"""

import os.path
import logging
import abc
import csv
import magic
import filecmp
import time

ALLOWED_PATHS = [
                # used for school.conf or *.csv in lmn_settings, lmn_devices and lmn_users
                '/etc/linuxmuster/sophomorix/',
                # used in lmn_linbo for start.conf
                '/srv/linbo',
                # used in lmn_settings for subnets configuration
                '/etc/linuxmuster/subnets-dev.csv'
                ]

class LMNFile(metaclass=abc.ABCMeta):
    """
    Meta class to handle all type of config file used in linuxmuster's project,
    e.g. ini, csv, linbo config files.
    """

    def __new__(cls, file, mode, delimiter=';', fieldnames=[]):
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

        ext = os.path.splitext(file)[-1]
        for child in cls.__subclasses__():
            if child.hasExtension(ext):
                obj = object.__new__(child)
                obj.__init__(file, mode, delimiter=';', fieldnames=[])
                return obj
        else:
            if filename.startswith('start.conf.'):
                # Linbo start.conf file
                obj = object.__new__(StartConfLoader)
                obj.__init__(file, mode, delimiter=';', fieldnames=[])
                return obj

    def __init__(self, file, mode, delimiter=';', fieldnames=[]):
        self.file = file
        self.opened = ''
        self.data = ''
        self.mode  = mode
        self.encoding = self.detect_encoding()
        self.comments = []
        self.check_allowed_path()
        self.delimiter = delimiter
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
    def __exit__(self):
        raise NotImplementedError

    def backup(self):
        """
        Create a backup of a file if in allowed paths, but on ly keeps 10 backups.
        Backup files names scheme is `.<name>.bak.<timestamp>`
        """

        if not os.path.exists(self.file):
            return

        dir, name = os.path.split(self.file)
        backups = sorted([x for x in os.listdir(dir) if x.startswith('.%s.bak.' % name)])
        while len(backups) > 10:
            os.unlink(os.path.join(dir, backups[0]))
            backups.pop(0)

        with open(dir + '/.' + name + '.bak.' + str(int(time.time())), 'w') as f:
            f.write(self.opened.read())

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
        else:
            raise IOError(_("Access refused."))

    def detect_encoding(self):
        """
        Try to detect encoding of the file through magic numbers.

        :return: Detected encoding
        :rtype: string
        """

        if not os.path.isfile(self.file):
            logging.info('Detected encoding for %s : no file, using utf-8', self.file)
            return 'utf-8'
        loader = magic.Magic(mime_encoding=True)
        encoding = loader.from_file(self.file)
        if 'ascii' in encoding or encoding == "binary":
            logging.info('Detected encoding for %s : ascii, but using utf-8', self.file)
            return 'utf-8'
        else:
            logging.info('Detected encoding for %s : %s', self.file, encoding)
            return encoding

class LinboLoader(LMNFile):
    """
    Handler for linbo's cloop informations files.
    """

    extensions = ['.desc', '.reg', '.postsync', '.info', '.macct']

    def __enter__(self):
        self.opened = open(self.file, self.mode, encoding=self.encoding)
        return self.opened

    def __exit__(self, *args):
        self.opened.close()

class CSVLoader(LMNFile):
    """
    Handler for csv files.
    """

    extensions = ['.csv']

    def __enter__(self):
        self.opened = open(self.file, 'r', encoding=self.encoding)
        if 'r' in self.mode or '+' in self.mode:
            self.data = csv.DictReader(
                (line for line in self.opened if not line.startswith('#')),
                delimiter = self.delimiter,
                fieldnames = self.fieldnames
            )
        return self

    def read(self):
        return list(self.data)

    def write(self, data):
        tmp = self.file + '_tmp'
        with open(tmp, 'w', encoding=self.encoding) as f:
            csv.DictWriter(
                f,
                delimiter=';',
                fieldnames = self.fieldnames
            ).writerows(data)
        if not filecmp.cmp(tmp, self.file):
            self.backup()
            os.rename(tmp, self.file)
        else:
            os.unlink(tmp)

    def __exit__(self, *args):
        if self.opened:
            self.opened.close()


"""LATER
class ConfigLoader(LMNFile):
    extensions = ['.ini', '.conf']


class StartConfLoader(LMNFile):
    extensions = []
"""