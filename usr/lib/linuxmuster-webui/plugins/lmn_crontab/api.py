#! /usr/bin/env python3

from datetime import datetime, date
import sys
from aj.plugins.lmn_common.api import lmconfig

class Holiday:
    def __init__(self, name, begin, end):
        """
        Holiday object.
        :param name: Name of holiday
        :type name: string
        :param begin: Begin as dd.mm.yyyy
        :type begin: string
        :param end: End as dd.mm.yyyy
        :type end: string
        """
        self.name = name
        self.begin = date(*map(int, begin.split('.')[::-1]))
        self.end = date(*map(int, end.split('.')[::-1]))

    def __str__(self):
        return self.name + ': ' + str(self.begin) + ' - ' + str(self.end)

def TestHolidays():
    """
    Method to get all holidays stored in lmconfig and test if the current day is in holiday.
    Method must be called in shell script e.g. crontab to exit if true.
    """
    today = date.today()

    holidays = []
    config = lmconfig.data['linuxmuster']['holidays']

    for name,period in config.items():
        begin, end = period.split('-')
        holidays.append(Holiday(name, begin, end))

    for holiday in holidays:
        if holiday.begin <= today <= holiday.end:
            sys.exit(-1)

    sys.exit()

