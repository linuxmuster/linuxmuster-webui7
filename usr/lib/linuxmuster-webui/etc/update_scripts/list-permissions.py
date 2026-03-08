#! /usr/bin/env python3

import os
import yaml


PLUGIN_PATH = '/usr/lib/linuxmuster-webui/plugins'
PERMISSIONS_TARGET = '/usr/lib/linuxmuster-webui/etc/default_permissions_keywords.yml'

permissions = {
    'globaladministrator': [],
    'schooladministrator': [],
    'teacher': [],
    'student': [],
    'parent': [],
    'staff': []
}

keywords = []

for plugin in os.listdir(PLUGIN_PATH):
    permissions_path = os.path.join(PLUGIN_PATH, plugin, 'permissions.yml')
    if os.path.isfile(permissions_path):
        with open(permissions_path) as tmp_data:
            tmp_permissions = yaml.load(tmp_data, Loader=yaml.SafeLoader)
        for role in tmp_permissions:
            perms = tmp_permissions.get(role, None)
            if perms:
                permissions[role].extend(perms)

            for perm in perms:
                keyword = perm.split(': ')[0]
                if keyword not in keywords and 'sidebar' not in keyword:
                    keywords.append(keyword)

with open(PERMISSIONS_TARGET, 'w') as target:
    for keyword in keywords:
        target.write(f"{keyword}:\n")
        authorized_roles = []
        for role in permissions.keys():
            if f'{keyword}: true' in permissions[role]:
                authorized_roles.append(role)
        target.write(f"- roles: {','.join(authorized_roles)}\n")
        target.write("- users: null\n")
        target.write("- groups: null\n")