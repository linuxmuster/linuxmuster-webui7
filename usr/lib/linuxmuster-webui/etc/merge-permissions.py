#! /usr/bin/env python3

import os
import yaml

PLUGIN_PATH = '/usr/lib/linuxmuster-webui/plugins'
PERMISSIONS_TARGET = '/usr/lib/linuxmuster-webui/etc/default-ui-permissions.ini'

permissions = {
    'globaladministrator': [],
    'schooladministrator': [],
    'teacher': [],
    'student': []
}

for plugin in os.listdir(PLUGIN_PATH):
    permissions_path = os.path.join(PLUGIN_PATH, plugin, 'permissions.yml')
    if os.path.isfile(permissions_path):
        with open(permissions_path) as tmp_data:
            tmp_permissions = yaml.load(tmp_data, Loader=yaml.SafeLoader)
        for role in tmp_permissions:
            if role in tmp_permissions and tmp_permissions[role]:
                permissions[role].extend(tmp_permissions[role])

with open(PERMISSIONS_TARGET, 'w') as target:
    for role in permissions.keys():
        target.write("\n")
        target.write(f"[{role}]\n")
        for permission in permissions[role]:
            target.write(f"    WEBUI_PERMISSIONS={permission}\n")




