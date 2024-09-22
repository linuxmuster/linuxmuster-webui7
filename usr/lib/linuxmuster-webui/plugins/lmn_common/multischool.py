import os
import yaml
import logging
from io import StringIO
from configobj import ConfigObj
from subprocess import check_output
from linuxmusterTools.samba_util import DriveManager, GPOManager
from linuxmusterTools.ldapconnector import LMNLdapReader as lr

from aj.plugins.lmn_common.api import samba_realm, samba_netbios, samba_override, lmn_getSophomorixValue
from aj.plugins.lmn_common.lmnfile import LMNFile


class SchoolManager:
    """
    In a multischool environment, it's necessary to have the possibility
    to switch between the differents schools configurations and specific options
    """

    def __init__(self):
        self.school = 'default-school'
        self.schools = [school['ou'] for school in lr.get('/schools')]
        self.schoolname = self.school
        self.schoolShare = f'\\\\{samba_realm}\\{self.school}\\'
        self.schoolGlobalShare = f'\\\\{samba_realm}\\linuxmuster-global\\'
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

    def get_schoolname_by_school(self, school):
        """
        Returns schoolname by school
        """


        try:
            with LMNFile(f'{self.configpath}school.conf', 'r') as f:
                return f.data['school']['SCHOOL_LONGNAME']
        except Exception:
            return None

    def get_schools(self):
        """
        Returns array of all schools with schoolname
        """

        allSchools = []
        for school in self.schools:
            allSchools.append({"school": school, "schoolname": self.get_schoolname_by_school(school)})
        return sorted(allSchools, key=lambda d: d['school'])

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

    def get_share_prefix(self, school=None):

        if school is None:
            school = self.school
            other_school = False
        else:
            other_school = True

        if school not in self.schools:
            return

        if school in self.dfs.keys():
            share_prefix = self.dfs[school]['dfs_proxy']
        elif samba_override['share_prefix']:
            share_prefix = f'\\\\{samba_override["share_prefix"]}\\{school}'
        else:
            share_prefix = f'\\\\{samba_netbios}\\{school}'

        if other_school:
            return share_prefix

        self.share_prefix = share_prefix

    def get_homepath(self, user_context):

        user = user_context['user']
        role = user_context['role']

        adminclass = user_context['adminclass']
        if self.school != 'default-school':
            # Remove prefix from adminclass in home path.
            adminclass = adminclass.lstrip(f"{self.school}-")

        if role == 'globaladministrator':
            home_path = f'\\\\{samba_netbios}\\linuxmuster-global\\management\\{user}'
        elif role == 'schooladministrator':
            home_path = f'{self.share_prefix}\\management\\{user}'
        elif role == "teacher":
            home_path = f'{self.share_prefix}\\{role}s\\{user}'
        else:
            home_path = f'{self.share_prefix}\\{role}s\\{adminclass}\\{user}'

        return home_path

    def get_shares(self, user_context):

        home_path = self.get_homepath(user_context)
        role = user_context['role']

        if role == 'globaladministrator':
            home_webdav = f"global/management/{user_context['user']}"
        else:
            home_webdav = home_path.replace(self.share_prefix, '').replace("\\", "/").strip('/')

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
            'webdav_url': home_webdav,
            'icon' : 'fas fa-home',
            'active': False,
        }
        linuxmuster_global = {
            'name' : 'Linuxmuster-Global',
            'path' : f'\\\\{samba_netbios}\\linuxmuster-global',
            'webdav_url': 'global',
            'icon' : 'fas fa-globe',
            'active': False,
        }
        school = {
            'name' : self.school,
            'path' : self.share_prefix,
            'webdav_url': self.school,
            'icon' : 'fas fa-school',
            'active': False,
        }
        all_schools = [
            {
            'name' : s,
            'path' : self.get_share_prefix(school=s),
            'webdav_url': s,
            'icon' : 'fas fa-school',
            'active': False,
            } for s in self.schools
        ]

        # teachers = {
        #     'name' : 'Teachers',
        #     'path' : f'{share_prefix}\\teachers',
        #     'webdav_url': f"teachers/",
        #     'icon' : 'fas fa-chalkboard-teacher',
        #     'active': False,
        # }
        students = {
            'name' : get_share_label('students', 'Students'),
            'path' : f'{self.share_prefix}\\students',
            'webdav_url': "students",
            'icon' : 'fas fa-user-graduate',
            'active': False,
            'id': 'students',
        }
        share = {
            'name' : get_share_label('share', 'Share'),
            'path' : f'{self.share_prefix}\\share',
            'webdav_url': "share",
            'icon' : 'fas fa-hand-holding',
            'active': False,
            'id': 'share',
        }
        program = {
            'name' : get_share_label('program', 'Programs'),
            'path' : f'{self.share_prefix}\\program',
            'webdav_url': "program",
            'icon' : 'fas fa-desktop',
            'active': False,
            'id': 'program',
        }
        iso = {
            'name' : get_share_label('iso', 'ISO'),
            'path' : f'{self.share_prefix}\\iso',
            'webdav_url': "iso",
            'icon' : 'fas fa-compact-disc',
            'active': False,
            'id': 'iso',
        }
        projects = {
            'name' : get_share_label('projects', 'Projects'),
            'path' : f'{self.share_prefix}\\share\\projects',
            'webdav_url': "share/projects",
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
            ] + all_schools,
            'schooladministrator': [
                home,
                school,
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
