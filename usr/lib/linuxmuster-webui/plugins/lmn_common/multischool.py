import os
import yaml
import logging
from io import StringIO
from configobj import ConfigObj
from subprocess import check_output

class SchoolManager():
    def __init__(self):
        self.school = 'default-school'
        self.get_configpath()
        self.load_school_dfs_shares()

    def load_custom_fields(self):
        config = f'/etc/linuxmuster/sophomorix/{self.school}/custom_fields.yml'
        self.custom_fields = {}
        if os.path.isfile(config):
            try:
                with open(config, 'r') as f:
                    self.custom_fields = yaml.load(f, Loader=yaml.SafeLoader)
            except Exception as e:
                logging.error(f"Could not load custom fields config: {e}")

    def load_holidays(self):
        config = f'/etc/linuxmuster/sophomorix/{self.school}/holidays.yml'
        self.holidays = {}
        if os.path.isfile(config):
            try:
                with open(config, 'r') as f:
                    self.holidays = yaml.load(f, Loader=yaml.SafeLoader)
            except Exception as e:
                logging.error(f"Could not load custom fields config: {e}")

    def get_configpath(self):
        """
        Return the default absolute path for config files in multischool env.
        """

        if self.school == "default-school":
            self.configpath = '/etc/linuxmuster/sophomorix/default-school/'
        else:
            self.configpath = f'/etc/linuxmuster/sophomorix/{self.school}/{self.school}.'

    def load_school_dfs_shares(self):
        """
        Read the output of 'net conf list' to get the share path, which could be
        different in case of DFS.
        """

        self.dfs = {}

        config = ConfigObj(StringIO(check_output(["/usr/bin/net", "conf", "list"], shell=False).decode()))
        for share_name, share_config in config.items():
            # DFS activated ?
            if share_config.get('msdfs_root', 'no') == 'yes':
                dfs_proxy = share_config.get('msdfs_proxy', '')
                if dfs_proxy != '':
                    # //sub.domain.lan/school to \\\\sub.domain.lan\\school
                    self.dfs[share_name] = {
                        'dfs_proxy': dfs_proxy.replace('/', '\\'),
                    }

    def switch(self, school):
        # Switch to another school
        self.school = school
        self.get_configpath()
        self.load_custom_fields()
        self.load_holidays()