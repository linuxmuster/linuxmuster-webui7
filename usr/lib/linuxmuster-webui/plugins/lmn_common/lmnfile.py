import os.path
import logging
import abc
import unicodecsv as csv
import magic

ALLOWED_PATHS = [
                # used for school.conf or *.csv in lmn_settings, lmn_devices and lmn_users
                '/etc/linuxmuster/sophomorix/',
                # used in lmn_linbo for start.conf
                '/srv/linbo',
                # used in lmn_settings for subnets configuration
                '/etc/linuxmuster/subnets-dev.csv'
                ]

class LMNFile(metaclass=abc.ABCMeta):
    def __new__(cls, file, mode):
        ext = os.path.splitext(file)[-1]
        for child in cls.__subclasses__():
            if child.hasExtension(ext):
                obj = object.__new__(child)
                obj.__init__(file, mode)
                return obj
        else:
            if filename.startswith('start.conf.'):
                # Linbo start.conf file
                obj = object.__new__(StartConfLoader)
                obj.__init__(file, mode)
                return obj

    def __init__(self, file, mode):
        self.file = file
        self.opened = ''
        self.mode  = mode
        self.encoding = self.detect_encoding()
        self.comments = []

    def read(self):
        if not self.opened:
            self.__enter__()
        return self.opened.read()

    def write(self):
        if not self.opened:
            self.__enter__()
        return self.opened.write()

    @classmethod
    def hasExtension(cls, ext):
        if ext in cls.extensions:
            return True
        return False

    @abc.abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(self):
        raise NotImplementedError

    # @abc.abstractmethod
    # def backup(self):
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def __iter__(self):
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def __next__(self):
    #     raise NotImplementedError

    def check_allowed_path(self):
        """Check path before modifying file for security reasons."""
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
        if not os.path.isfile(self.file):
            logging.info('Detected encoding for %s : no file, using utf-8', self.file)
            return 'utf-8'
        loader = magic.Magic(mime_encoding=True)
        encoding = loader.from_file(self.file)
        if 'ascii' in encoding:
            logging.info('Detected encoding for %s : ascii, but using utf-8', self.file)
            return 'utf-8'
        else:
            logging.info('Detected encoding for %s : %s', self.file, encoding)
            return encoding

class LinboLoader(LMNFile):
    extensions = ['.desc', '.reg', '.postsync', '.info', '.macct']

    def __enter__(self):
        self.opened = open(self.file, self.mode, encoding=self.encoding)
        return self.opened

    def __exit__(self, *args):
        self.opened.close()

"""LATER
class CSVLoader(LMNFile):
    extensions = ['.csv']

    def __enter__(self):
        self.opened = open(self.file, self.mode, encoding=self.encoding)
        return self.opened

    def __exit__(self, *args):
        self.opened.close()

    def __iter__(self):
        return self

    def __next__(self):
        # Store comments in self.comments
        nextline = self.opened.readline()
        if nextline == '':
            raise StopIteration()
        while nextline.startswith('#'):
            self.comments.append(nextline)
            nextline = self.opened.readline()
        # Reader is unicodecsv, which needs bytes
        return nextline.encode('utf-8').strip()

class ConfigLoader(LMNFile):
    extensions = ['.ini', '.conf']


class StartConfLoader(LMNFile):
    extensions = []
"""