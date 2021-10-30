#! /usr/bin/env python3

import os
from collections import OrderedDict
from configparser import ConfigParser, NoOptionError

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super().__setitem__(key, value)

    @staticmethod
    def getlist(value):
        return value.split(os.linesep)

permissions = {
    'globaladministrator': [],
    'schooladministrator': [],
    'teacher': [],
    'student': []
}
permissions_target = 'default-ui-permissions-tests.ini'

for plugin in os.listdir('../plugins'):
    permissions_path = os.path.join('../plugins', plugin, 'permissions.ini')
    if os.path.isfile(permissions_path):
        tmp_permissions = ConfigParser(dict_type=MultiOrderedDict, strict=False,
                                   converters={
                                       'list': MultiOrderedDict.getlist})
        tmp_permissions.read(permissions_path)
        for role in permissions.keys():
            try:
                permissions_list = tmp_permissions.getlist(role, "webui_permissions")
            except NoOptionError:
                permissions_list = []
            permissions[role].extend(permissions_list)

with open(permissions_target, 'w') as target:
    for role in permissions.keys():
        target.write(f"[{role}]\n")
        for permission in permissions[role]:
            target.write(f"\tWEBUI_PERMISSIONS={permission}\n")




