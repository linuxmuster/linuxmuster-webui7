# coding=utf-8
import os
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lm_common.api import lm_backup_file
from aj.plugins.lm_common.api import lmn_getSophomorixValue
from configparser import ConfigParser

class IniParser(ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d


@component(HttpPlugin)
class Handler(HttpPlugin):
    EMAIL_MAPPING = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss',
        '@': '\\@',
    }
    EMAIL_REVERSE_MAPPING = dict(
        (v, k) for (k, v) in EMAIL_MAPPING.items()
    )

    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/schoolsettings/determine-encoding')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_session_sessions(self, http_context):
        fileToCheck = http_context.json_body()['path']
        sophomorixCommand = ['sophomorix-check', '--analyze-encoding', fileToCheck, '-jj']
        encoding = lmn_getSophomorixValue(sophomorixCommand, 'SUMMARY/0/ANALYZE-ENCODING/ENCODING')
        return encoding


    @url(r'/api/lm/schoolsettings')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_settings(self, http_context):
        school = 'default-school'
        path = '/etc/linuxmuster/sophomorix/'+school+'/school.conf'
        if http_context.method == 'GET':
            # Parse csv config file
            config = ConfigParser()
            config.read(path)
            settings = {}
            for section in config.sections():
                settings[section] = {}
                for (key, val) in config.items(section):
                   if val.isdigit():
                      val = int(val)
                      #settings[section][key] = val
                   if val == 'no':
                        val = False
                   if val == 'yes':
                        val = True
                   settings[section][key] = val
            return settings


        if http_context.method == 'POST':
            content = ''
            data = http_context.json_body()
            if 'admins_print' in data:
                for k, v in self.EMAIL_MAPPING.items():
                    data['admins_print'] = data['admins_print'].replace(k, v)

            def convert_value(v):
                if type(v) is int:
                    return str(v)
                elif type(v) is bool:
                    return 'yes' if v else 'no'
                else:
                    return '%s' % v

            section_name = ''
            set_control = 0
            for line in open(path):
                originalLine = line
                # remove everything before comment
                if '#' in line:
                    line = line.split('#',1)[1]
                    line = '#'+line
                if line.startswith('#'):
                    content += originalLine
                    continue
                # if new section found
                if line.startswith('['):
                    # check if last section contained all keys
                    if set_control is 1:
                        for k in data[section_name]:
                            if k not in keys_found:
                                k = k.strip()
                                v = v.strip()
                                content += "\t%s = %s\n" % (k.upper(), convert_value(data[section_name][k]))
                    # start of with new section
                    set_control = 1
                    keys_found = []
                    section_name = line.strip('[]\n')
                else:
                    k, v = line.split('=', 1)
                    k = k.strip().lower()
                    v = v.strip()
                    if k in data[section_name]:
                        newValue = convert_value(data[section_name][k])
                        keys_found.append(k)

                        originalLine = originalLine.replace(v, newValue)
                        if newValue not in v:
                            originalLine = originalLine.lstrip('#')
                content += originalLine


            lm_backup_file(path)
            with open(path, 'w') as f:
                f.write(content)

    @url(r'/api/lm/schoolsettings/school-share')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_school_share(self, http_context):
        school = 'default-school'
        path = '/srv/samba/schools/'+school+'/share'
        if http_context.method == 'GET':
            print os.stat(path).st_mode
            return os.stat(path).st_mode & 0o3777 == 0o3777
        else:
            if http_context.json_body():
                os.chmod(path, 0o3777)
            else:
                os.chmod(path, 0o0700)
