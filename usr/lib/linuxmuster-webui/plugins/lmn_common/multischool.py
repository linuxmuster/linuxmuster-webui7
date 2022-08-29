import os
import yaml
import logging
from io import StringIO
from configobj import ConfigObj
from subprocess import check_output

from aj.plugins.lmn_common.api import samba_domain


class SchoolManager():
    def __init__(self):
        self.school = 'default-school'
        self.load()

    def load(self):
        self.get_configpath()
        self.load_custom_fields()
        self.load_holidays()
        self.load_school_dfs_shares()
        self.get_share_prefix()

    def switch(self, school):
        # Switch to another school
        if school != self.school:
            self.school = school
            self.load()

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

    def get_share_prefix(self):

        if self.school in self.dfs.keys():
            self.share_prefix = self.dfs[self.school]['dfs_proxy']
        else:
            self.share_prefix = f'\\\\{samba_domain}\\{self.school}'

    def get_homepath(self, user, role, adminclass):

        if role == 'globaladministrator':
            home_path = f'\\\\{samba_domain}\\linuxmuster-global\\management\\{user}'
        elif role == 'schooladministrator':
            home_path = f'{self.share_prefix}\\management\\{user}'
        elif role == "teacher":
            home_path = f'{self.share_prefix}\\{role}s\\{user}'
        else:
            home_path = f'{self.share_prefix}\\{role}s\\{adminclass}\\{user}'

        return home_path

    def get_shares(self, user, role, adminclass):

        home_path = self.get_homepath(user, role, adminclass)

        home = {
            'name' : 'Home',
            'path' : home_path,
            'icon' : 'fas fa-home',
            'active': False,
        }
        linuxmuster_global = {
            'name' : 'Linuxmuster-Global',
            'path' : f'\\\\{samba_domain}\\linuxmuster-global',
            'icon' : 'fas fa-globe',
            'active': False,
        }
        all_schools = {
            'name' : self.school,
            'path' : self.share_prefix,
            'icon' : 'fas fa-school',
            'active': False,
        }
        # teachers = {
        #     'name' : 'Teachers',
        #     'path' : f'{share_prefix}\\teachers',
        #     'icon' : 'fas fa-chalkboard-teacher',
        #     'active': False,
        # }
        students = {
            'name' : 'Students',
            'path' : f'{self.share_prefix}\\students',
            'icon' : 'fas fa-user-graduate',
            'active': False,
        }
        share = {
            'name' : 'Share',
            'path' : f'{self.share_prefix}\\share',
            'icon' : 'fas fa-hand-holding',
            'active': False,
        }
        program = {
            'name' : 'Programs',
            'path' : f'{self.share_prefix}\\program',
            'icon' : 'fas fa-desktop',
            'active': False,
        }
        # iso = {
        #     'name' : 'ISO',
        #     'path' : f'{share_prefix}\\iso',
        #     'icon' : 'fas fa-compact-disc',
        #     'active': False,
        # }

        shares = {
            'globaladministrator': [
                home,
                linuxmuster_global,
                all_schools,
            ],
            'schooladministrator': [
                home,
                all_schools,
            ],
            'teacher': [
                home,
                students,
                program,
                share,
            ],
            'student': [
                home,
                share,
                program,
            ]
        }

        return shares[role]