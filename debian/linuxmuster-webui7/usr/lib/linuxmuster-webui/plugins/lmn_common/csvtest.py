import unicodecsv as csv
#from api import CSVSpaceStripper

import os

class CSVSpaceStripper:
    def __init__(self, file, encoding):
        self.f = file
        self.encoding = encoding='utf-8'

    def close(self):
        self.f.close()

    def __iter__(self):
        return self

    def next(self):
        return self.f.next().decode(encoding='utf-8', errors='ignore').strip()
        #return self.f.next().decode(self.encoding, errors='ignore').strip()



path = '/etc/linuxmuster/sophomorix/default-school/teachers.csv'
fieldnames = [
    'class',
    'last_name',
    'first_name',
    'birthday',
    'login',
    'password',
    'usertoken',
    'quota',
    'mailquota',
    'reserved',
]


print list(
    csv.DictReader(
        CSVSpaceStripper(
            open(path),
            encoding='utf-8'
        ),
        delimiter=';',
        fieldnames=fieldnames
    )
)

