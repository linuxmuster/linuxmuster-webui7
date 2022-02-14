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
import re
from glob import glob
from configparser import ConfigParser

from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import authorize
from aj.plugins.lmn_common.lmnfile import LMNFile
from aj.plugins.lmn_common.api import lmn_get_school_configpath
from aj.plugins.lmn_common.multischool import School
from aj.plugins.lmn_common.api import lmconfig


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

    def _filter_templates(self, filename, school=''):
        """
        Test if the name respects the sophomorix scheme for latex templates.
        See https://github.com/linuxmuster/sophomorix4/blob/bionic/sophomorix-samba/lang/latex/README.latextemplates.

        :param school: school
        :type school: string
        :param file: name of the file
        :type file: string
        :return: result of the test
        :rtype: dict with groups values
        """

        pattern = re.compile(
            school + r'\.?([^-]*)-([A-Z]+)-(\d+)-template\.tex')
        m = re.match(pattern, filename)
        if m is None:
            return None
        data = m.groups()
        template = {
            'filename': filename,
            'name': data[0],
            'lang': data[1],
            'numberPerPage': int(data[2])
        }
        return template

    @url(r'/api/lm/schoolsettings/latex-templates')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_latex_template(self, http_context):
        """
        Get list of latex templates for printing with sophomorix.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        templates_multiple = []
        templates_individual = []
        sophomorix_default_path = '/usr/share/sophomorix/lang/latex/templates/'

        for path in glob(sophomorix_default_path + "*tex"):
            filename = path.split('/')[-1]
            template = self._filter_templates(filename)
            if template:
                template['path'] = path
                if template['numberPerPage'] > 1:
                    templates_multiple.append(template)
                else:
                    templates_individual.append(template)

        # School defined templates
        school = School.get(self.context).school
        custom_templates_path = f'/etc/linuxmuster/sophomorix/{school}/latex-templates/'
        if os.path.isdir(custom_templates_path):
            for path in glob(custom_templates_path + "*tex"):
                filename = path.split('/')[-1]
                template = self._filter_templates(filename, school)
                if template:
                    template['path'] = os.path.join(custom_templates_path, filename)
                    if template['numberPerPage'] > 1:
                        templates_multiple.append(template)
                    else:
                        templates_individual.append(template)

        return templates_individual, templates_multiple

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
    @authorize('lm:globalsettings')
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
                'passwordTemplates': lmconfig.get('passwordTemplates', {'multiple': {}, 'individual': {}}),
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
            lmconfig['passwordTemplates'] = custom_config['passwordTemplates']
            with LMNFile('/etc/linuxmuster/webui/config.yml', 'w') as webui:
                webui.write(lmconfig)

    @url(r'/api/lm/holidays')
    @authorize('lm:schoolsettings')
    @endpoint(api=True)
    def handle_api_holidays(self, http_context):
        """
        Manage `holidays.yml` config file for holidays.
        Method GET: read content.
        Method POST: write new content.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Settings in read mode
        :rtype: dict
        """

        # TODO : school = 'default-school'
        path = '/etc/linuxmuster/holidays.yml'

        if http_context.method == 'GET':
            try:
                with LMNFile(path, 'r') as s:
                    return [{
                        'name': name,
                        'start': dates['start'],
                        'end': dates['end'],
                    } for name, dates in s.data.items()]
            except AttributeError:
                return []

        if http_context.method == 'POST':
            data = http_context.json_body()
            holidays = {holiday['name']: {
                'start': holiday['start'],
                'end': holiday['end']}
                for holiday in data
            }
            with LMNFile(path, 'w') as f:
                f.write(holidays)
