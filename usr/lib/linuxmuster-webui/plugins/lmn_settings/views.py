"""
Module to configure sophomorix.
"""

# coding=utf-8
import os
import unicodecsv as csv
import subprocess
import filecmp
from datetime import datetime
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import authorize
from aj.plugins.lmn_common.lmnfile import LMNFile
from aj.plugins.lmn_common.api import lmn_get_school_configpath
from aj.plugins.lmn_common.multischool import School
from aj.plugins.lmn_common.api import lmconfig
from configparser import ConfigParser


@component(HttpPlugin)
class Handler(HttpPlugin):
    EMAIL_MAPPING = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss',
        '@': '\\@',
    }
    EMAIL_REVERSE_MAPPING = { v:k for (k, v) in EMAIL_MAPPING.items()}

    def __init__(self, context):
        self.context = context


    @url(r'/api/lmn/schoolsettings/determine-encoding')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_session_sessions(self, http_context):
        """
        Determine encoding using sophomorix-check.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Encoding type of the file, e.g. utf-8
        :rtype: string
        """

        fileToCheck = http_context.json_body()['path']
        if os.path.isfile(fileToCheck) is False:
            os.mknod(fileToCheck)
        if os.path.isfile(fileToCheck):
            with LMNFile(fileToCheck, 'r') as f:
                return f.detect_encoding()
        return None


    @url(r'/api/lm/schoolsettings')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_settings(self, http_context):
        """
        Read and write the config file `school.conf`.
        Method GET: read the file.
        Method POST: write the new content.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Settings in read mode
        :rtype: dict in read mode
        """

        school = School.get(self.context).school
        path = lmn_get_school_configpath(school)+'school.conf'
        # Update each time the config_obj because it may have changed
        with LMNFile(path, 'r') as f:
            self.config_obj = f

        if http_context.method == 'GET':
            # Just export ConfigObj as dict for angularjs
            return dict(self.config_obj.data)

        if http_context.method == 'POST':
            data = http_context.json_body()
            if 'admins_print' in data:
                for k, v in self.EMAIL_MAPPING.items():
                    data['admins_print'] = data['admins_print'].replace(k, v)

            self.config_obj.write(data)

            # Update setup.ini with new schoolname
            with LMNFile('/var/lib/linuxmuster/setup.ini', 'r') as s:
                s.data['setup']['schoolname'] = data['school']['SCHOOL_LONGNAME']
                s.write(s.data)


    @url(r'/api/lm/schoolsettings/school-share')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_school_share(self, http_context):
        """
        DEPRECATED, not used anymore. Adapt owner and group rights
        on a share directory.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        school = 'default-school'
        path = '/srv/samba/schools/'+school+'/share'
        if http_context.method == 'GET':
            print(os.stat(path).st_mode)
            return os.stat(path).st_mode & 0o3777 == 0o3777

        if http_context.json_body():
            os.chmod(path, 0o3777)
        else:
            os.chmod(path, 0o0700)

    @url(r'/api/lm/subnets')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_subnet(self, http_context):
        """
        Manage `subnets.csv` config file for subnets.
        Method GET: read content.
        Method POST: write new content.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Settings in read mode
        :rtype: dict
        """

        # TODO : school = 'default-school'
        path = '/etc/linuxmuster/subnets.csv'
        fieldnames = [
            'network',
            'routerIp',
            'beginRange',
            'endRange',
            'setupFlag',
        ]
        if http_context.method == 'GET':
            with LMNFile(path, 'r', fieldnames=fieldnames) as s:
                subnets = list(s.data)
            return subnets

        if http_context.method == 'POST':
            data = http_context.json_body()
            with LMNFile(path, 'w', fieldnames=fieldnames) as f:
                f.write(data)

            try:
                subprocess.check_call('linuxmuster-import-subnets > /tmp/import_devices.log', shell=True)
            except Exception as e:
                raise EndpointError(None, message=str(e))

    @url(r'/api/lm/read_custom_config')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_read_custom_config(self, http_context):
        """
        Read webui yaml config and return the settings for custom fields.
        Method GET: read content.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Settings in read mode
        :rtype: dict
        """

        if http_context.method == 'GET':
            return {
                'custom': lmconfig.get('custom', {}),
                'customMulti': lmconfig.get('customMulti', {}),
                'customDisplay': lmconfig.get('customDisplay', {}),
                'proxyAddresses': lmconfig.get('proxyAddresses', {}),
            }


    @url(r'/api/lm/save_custom_config')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_save_custom_config(self, http_context):
        """
        Save customs sophomorix fields settings in the webui yaml config.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return:
        :rtype:
        """

        if http_context.method == 'POST':
            custom_config = http_context.json_body()['config']
            lmconfig['custom'] = custom_config['custom']
            lmconfig['customMulti'] = custom_config['customMulti']
            lmconfig['customDisplay'] = custom_config['customDisplay']
            lmconfig['proxyAddresses'] = custom_config['proxyAddresses']
            with LMNFile('/etc/linuxmuster/webui/config.yml', 'w') as webui:
                webui.write(lmconfig)
