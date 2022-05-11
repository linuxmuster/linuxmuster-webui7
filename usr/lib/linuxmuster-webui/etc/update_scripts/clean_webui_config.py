#! /usr/bin/env python3

"""
Above version 7.1.11:
 * Remove deprecated options (initialized, is-configured, provision)
 * Split custom fields from config.yml to /etc/linuxmuster/sophomorix/default-school
"""

import yaml

WEBUI_CONFIG = '/etc/linuxmuster/webui/config.yml'
CUSTOM_FIELDS_CONFIG = '/etc/linuxmuster/sophomorix/default-school/custom_fields.yml'
CUSTOM_FIELDS_DICT = {}

with open(WEBUI_CONFIG, 'r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

for key in ['initialized', 'is-configured', 'provision']:
    if key in config['linuxmuster'].keys():
        del config['linuxmuster'][key]

for key in ['custom', 'customDisplay', 'customMulti', 'proxyAddresses']:
    if key in config.keys():
        CUSTOM_FIELDS_DICT[key] = config[key]
        del config[key]

if CUSTOM_FIELDS_DICT:
    with open(CUSTOM_FIELDS_CONFIG, 'w') as f:
        f.write(
            yaml.safe_dump(
                CUSTOM_FIELDS_DICT,
                default_flow_style=False,
                encoding='utf-8',
                allow_unicode=True
            ).decode('utf-8'))
else:
    if 'passwordTemplates' in config.keys():
        with open(CUSTOM_FIELDS_CONFIG, 'r') as f:
            CUSTOM_FIELDS_DICT = yaml.load(f, Loader=yaml.SafeLoader)
        CUSTOM_FIELDS_DICT['passwordTemplates'] = config['passwordTemplates']
        del config['passwordTemplates']
        with open(CUSTOM_FIELDS_CONFIG, 'w') as f:
            f.write(
                yaml.safe_dump(
                    CUSTOM_FIELDS_DICT,
                    default_flow_style=False,
                    encoding='utf-8',
                    allow_unicode=True
                ).decode('utf-8'))

with open(WEBUI_CONFIG, 'w') as f:
    f.write(
        yaml.safe_dump(
            config,
            default_flow_style=False,
            encoding='utf-8',
            allow_unicode=True
        ).decode('utf-8'))


