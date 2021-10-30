#! /usr/bin/env python3

import os
import yaml

permissions = {
    'globaladministrator': [],
    'schooladministrator': [],
    'teacher': [],
    'student': []
}
permissions_target = 'default-ui-permissions-tests.ini'

for plugin in os.listdir('../plugins'):
    permissions_path = os.path.join('../plugins', plugin, 'permissions.yml')
    if os.path.isfile(permissions_path):
        with open(permissions_path) as tmp_data:
            tmp_permissions = yaml.load(tmp_data, Loader=yaml.SafeLoader)
        for role in tmp_permissions:
            permissions[role].extend(tmp_permissions[role])

with open(permissions_target, 'w') as target:
    for role in permissions.keys():
        target.write("\n")
        target.write(f"[{role}]\n")
        for permission in permissions[role]:
            target.write(f"\tWEBUI_PERMISSIONS={permission}\n")




