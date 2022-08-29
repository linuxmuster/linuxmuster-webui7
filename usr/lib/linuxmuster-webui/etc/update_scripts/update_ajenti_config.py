#! /usr/bin/env python3

import yaml

# Read actual config file
with open('/etc/ajenti/config.yml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)

# Add new email parameter for Ajenti 2.1.44
config.setdefault('email', {})
config['email'].setdefault('enable', False)
config['email'].setdefault('templates', {})
config['email']['templates'].setdefault('reset_email', '/etc/linuxmuster/webui/email_templates/reset_email.html')
config.setdefault('logo', '/usr/lib/linuxmuster-webui/plugins/lmn_common/resources/img/logo-full.png')

# Fix hyphen to underscore in previous versions
if config['email']['templates']['reset_email'] == '/etc/linuxmuster/webui/email-templates/reset_email.html':
    config['email']['templates']['reset_email'] = '/etc/linuxmuster/webui/email_templates/reset_email.html'

# Add new custom main view for Ajenti 2.2.1
config.setdefault('view', {})
config['view'].setdefault('plugin', 'lmn_common')
config['view'].setdefault('filepath', 'resources/content/main_view.html')

# Write new config file
with open('/etc/ajenti/config.yml', 'w') as config_file:
    config_file.write(
        yaml.safe_dump(
            config,
            default_flow_style=False,
            encoding='utf-8',
            allow_unicode=True
        ).decode('utf-8'))



