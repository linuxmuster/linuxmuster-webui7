import os
import yaml
import logging
from io import StringIO
from configobj import ConfigObj
from subprocess import check_output
from linuxmusterTools.sambaTool import DriveManager, GPOManager

from aj.plugins.lmn_common.api import samba_realm, samba_netbios, samba_override, lmn_getSophomorixValue
from aj.plugins.lmn_common.lmnfile import LMNFile


class SchoolManager:
    """
    In a multischool environment, it's necessary to have the possibility
    to switch between the differents schools configurations and specific options
    """

    def __init__(self):
        self.school = 'default-school'
        self.schoolname = self.school
        self.schoolShare = f'\\\\{samba_realm}\\{self.school}\\'
        self.gpomgr = GPOManager()
        self.load()

    def load(self):
        """
        Main method of the object : load all schools specific options when
        switching to another school.
        """

        self.get_configpath()
        self.load_custom_fields()
        self.load_holidays()
        self.load_school_dfs_shares()
        self.get_share_prefix()
        self.load_drives()
        self.get_schoolname()

    def switch(self, school):
        """
        Switch to another school and then reload all configurations.
        """

        if school != self.school:
            self.school = school
            self.schoolShare = f'\\\\{samba_realm}\\{self.school}\\'
            self.load()

    def load_custom_fields(self):
        """
        Load custom fields configurations.
        """

        config = f'/etc/linuxmuster/sophomorix/{self.school}/custom_fields.yml'
        self.custom_fields = {}
        if os.path.isfile(config):
            try:
                with open(config, 'r') as f:
                    self.custom_fields = yaml.load(f, Loader=yaml.SafeLoader)
            except Exception as e:
                logging.error(f"Could not load custom fields config: {e}")

    def load_holidays(self):
        """
        Load holidays configurations.
        """

        config = f'/etc/linuxmuster/sophomorix/{self.school}/holidays.yml'
        self.holidays = {}
        if os.path.isfile(config):
            try:
                # Enforce read permissions for crontab users
                os.chmod(config, 0o644)
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

    def get_schoolname(self):
        """
        Read the school name from school.conf.
        """


        try:
            with LMNFile(f'{self.configpath}school.conf', 'r') as f:
                self.schoolname = f.data['school']['SCHOOL_LONGNAME']
        except Exception:
            pass

    def load_school_dfs_shares(self):
        """
        Read the output of 'net conf list' to get the share path, which could be
        different in case of DFS.
        """

        self.dfs = {}

        config = ConfigObj(StringIO(check_output(["/usr/bin/net", "conf", "list"], shell=False).decode()))
        for share_name, share_config in config.items():
            # DFS activated ?
            if share_config.get('msdfs root', 'no') == 'yes':
                dfs_proxy = share_config.get('msdfs proxy', '')
                if dfs_proxy != '':
                    # //sub.domain.lan/school to \\\\sub.domain.lan\\school
                    self.dfs[share_name] = {
                        'dfs_proxy': dfs_proxy.replace('/', '\\'),
                    }

    def load_drives(self):
        """
        Load Drives.xml content from school policies
        """

        self.gpo = self.gpomgr.gpos.get(f"sophomorix:school:{self.school}", None)
        if self.gpo:
            self.drivemgr = self.gpo.drivemgr
        else:
            self.drivemgr = DriveManager(None)

        self.drives = self.drivemgr.drives

    def get_share_prefix(self):

        if self.school in self.dfs.keys():
            self.share_prefix = self.dfs[self.school]['dfs_proxy']
        elif samba_override['share_prefix']:
            self.share_prefix = f'\\\\{samba_override["share_prefix"]}\\{self.school}'
        else:
            self.share_prefix = f'\\\\{samba_netbios}\\{self.school}'

    def get_homepath(self, user_context):

        if samba_override['share_prefix']:
            user = user_context['user']
            role = user_context['role']
            adminclass = user_context['adminclass']
            if role == 'globaladministrator':
                home_path = f'\\\\{samba_override["share_prefix"]}\\linuxmuster-global\\management\\{user}'
            elif role == 'schooladministrator':
                home_path = f'{self.share_prefix}\\management\\{user}'
            elif role == "teacher":
                home_path = f'{self.share_prefix}\\{role}s\\{user}'
            else:
                home_path = f'{self.share_prefix}\\{role}s\\{adminclass}\\{user}'
        else:
            home_path = user_context['home']

        return home_path

    def get_shares(self, user_context):

        home_path = self.get_homepath(user_context)
        role = user_context['role']

        def get_share_label(share_name, default):
            for drive in self.drives:
                if share_name == drive.id:
                    return drive.label or default

        def get_share_disabled(share_id):
            for drive in self.drives:
                if share_id == drive.id:
                    return drive.disabled

        home = {
            'name' : 'Home',
            'path' : home_path,
            'icon' : 'fas fa-home',
            'active': False,
        }
        linuxmuster_global = {
            'name' : 'Linuxmuster-Global',
            'path' : f'\\\\{samba_netbios}\\linuxmuster-global',
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
            'name' : get_share_label('students', 'Students'),
            'path' : f'{self.share_prefix}\\students',
            'icon' : 'fas fa-user-graduate',
            'active': False,
            'id': 'students',
        }
        share = {
            'name' : get_share_label('share', 'Share'),
            'path' : f'{self.share_prefix}\\share',
            'icon' : 'fas fa-hand-holding',
            'active': False,
            'id': 'share',
        }
        program = {
            'name' : get_share_label('program', 'Programs'),
            'path' : f'{self.share_prefix}\\program',
            'icon' : 'fas fa-desktop',
            'active': False,
            'id': 'program',
        }
        iso = {
            'name' : get_share_label('iso', 'ISO'),
            'path' : f'{self.share_prefix}\\iso',
            'icon' : 'fas fa-compact-disc',
            'active': False,
            'id': 'iso',
        }
        projects = {
            'name' : get_share_label('projects', 'Projects'),
            'path' : f'{self.share_prefix}\\share\\projects',
            'icon' : 'fas fa-atlas',
            'active': False,
            'id': 'projects',
        }

        standard_shares = {
            'projects': projects,
            'iso': iso,
            'program': program,
            'share':share,
            'students':students,
        }

        roles_shares = {
            'globaladministrator': [
                home,
                linuxmuster_global,
                all_schools,
            ],
            'schooladministrator': [
                home,
                all_schools,
            ]
            ,
            'teacher': [
                home,
            ],
            'student': [
                home,
            ]
        }

        # TODO: Use visible method from lmntools, but first when it interprets
        # the filter correctly. Something like:
        # drive.visible(user)
        # where user is a user object from ldapreader, containing all infos.
        # TODO: Missing user defined shares
        for share_id,standard_share in standard_shares.items():
            # This basic test only get the disabled attribute.
            if share_id != 'students':
                if not get_share_disabled(share_id):
                    roles_shares['teacher'].append(standard_share)
                    roles_shares['student'].append(standard_share)

        if not get_share_disabled('students'):
            roles_shares['teacher'].append(students)

        return roles_shares[role]
