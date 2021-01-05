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
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_write_configfile, lmn_getSophomorixValue, CSVSpaceStripper, lmn_write_csv, lmn_backup_file
from aj.plugins.lmn_common.lmnfile import LMNFile
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
        #     sophomorixCommand = ['sophomorix-check', '--analyze-encoding', fileToCheck, '-jj']
        #     encoding = lmn_getSophomorixValue(sophomorixCommand, 'SUMMARY/0/ANALYZE-ENCODING/ENCODING')
        #     return encoding
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

        school = 'default-school'
        path = '/etc/linuxmuster/sophomorix/'+school+'/school.conf'
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

        school = 'default-school'
        path = '/etc/linuxmuster/subnets.csv'
        fieldnames = [
            'network',
            'routerIp',
            'beginRange',
            'endRange',
            'setupFlag',
        ]
        if http_context.method == 'GET':
            return list(
                csv.DictReader(CSVSpaceStripper(open(path)), delimiter=';', fieldnames=fieldnames)
            )
        if http_context.method == 'POST':
            data = http_context.json_body()
            header = """
# modified by Webui at %s
# /etc/linuxmuster/subnets.csv
#
# thomas@linuxmuster.net
#
# Network/Prefix ; Router-IP (last available IP in network) ; 1. Range-IP ; Last-Range-IP ; SETUP-Flag
#
# server subnet definition
""" % (datetime.now().strftime("%Y%m%d%H%M%S"))
            separator = """
# add your subnets below
#
"""
            tmp = path + '_tmp'
            with open(tmp, 'w') as f:
                f.write(header)
                # Write setup subnet : Sure that data[0] contains the setup subnet ?
                csv.DictWriter(
                    f,
                    delimiter=';',
                    fieldnames=fieldnames,
                    #encoding='utf-8'
                ).writerows([data[0]])
                # Write custom subnets
                f.write(separator)
                csv.DictWriter(
                    f,
                    delimiter=';',
                    fieldnames=fieldnames,
                    #encoding='utf-8'
                ).writerows(data[1:])
            if not filecmp.cmp(tmp, path):
                lmn_backup_file(path)
                os.rename(tmp, path)
            else:
                os.unlink(tmp)
            try:
                subprocess.check_call('linuxmuster-import-subnets > /tmp/import_devices.log', shell=True)
            except Exception as e:
                raise EndpointError(None, message=str(e))
