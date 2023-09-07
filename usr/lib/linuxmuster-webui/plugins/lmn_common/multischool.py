import os
import yaml
import logging
from io import StringIO
from configobj import ConfigObj
from subprocess import check_output
import xml.etree.ElementTree as ElementTree

from aj.plugins.lmn_common.api import samba_realm, lmn_getSophomorixValue


class Drives:
    """Object to store data from dDrives.xml"""

    def __init__(self, policy):
        self.policy = policy
        self.path = f'/var/lib/samba/sysvol/{samba_realm}/Policies/{self.policy}/User/Preferences/Drives/Drives.xml'
        self.usedLetters = []
        self.load()

    def load(self):
        self.drives = []
        self.drives_dict = {}

        try:
            self.tree = ElementTree.parse(self.path)
        except FileNotFoundError:
            return

        for drive in self.tree.findall('Drive'):
            drive_attr = {'properties': {}}
            drive_attr['disabled'] = bool(int(drive.attrib.get('disabled', '0')))
            for prop in drive.findall('Properties'):
                drive_attr['properties']['useLetter'] = bool(int(prop.get('useLetter', '0')))
                drive_attr['properties']['letter'] = prop.get('letter', '')
                drive_attr['properties']['label'] = prop.get('label', 'Unknown')
                drive_attr['properties']['path'] = prop.get('path', None)
                self.usedLetters.append(drive_attr['properties']['letter'])

            self.drives.append(drive_attr)
            if drive_attr['properties']['path'] is not None:
                drive_id = drive_attr['properties']['path'].split('\\')[-1]
                self.drives_dict[drive_id] = {
                    'userLetter': drive_attr['properties']['useLetter'],
                    'letter': drive_attr['properties']['letter'],
                    'disabled': drive_attr['disabled'],
                    'label': drive_attr['properties']['label'],
                }

    def save(self, content):
        self.tree.write(f'{self.path}.bak', encoding='utf-8', xml_declaration=True)

        for drive in self.tree.findall('Drive'):
            for prop in drive.findall('Properties'):
                for newDrive in content:
                    if newDrive['properties']['label'] == prop.get('label', 'Unknown'):
                        prop.set('letter', newDrive['properties']['letter'])
                        prop.set('useLetter', str(int(newDrive['properties']['useLetter'])))
                        drive.set('disabled', str(int(newDrive['disabled'])))

        self.tree.write(self.path, encoding='utf-8', xml_declaration=True)
        self.load()

class SchoolManager:
    def __init__(self):
        self.school = 'default-school'
        self.schoolShare = f'\\\\{samba_realm}\\{self.school}\\'
        self.policy = ''
        self.load()

    def load(self):
        self.get_configpath()
        self.load_custom_fields()
        self.load_holidays()
        self.load_school_dfs_shares()
        self.get_share_prefix()
        self.load_gpo_list()
        self.load_drives()

    def switch(self, school):
        # Switch to another school
        if school != self.school:
            self.school = school
            self.schoolShare = f'\\\\{samba_realm}\\{self.school}\\'
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
            if share_config.get('msdfs root', 'no') == 'yes':
                dfs_proxy = share_config.get('msdfs proxy', '')
                if dfs_proxy != '':
                    # //sub.domain.lan/school to \\\\sub.domain.lan\\school
                    self.dfs[share_name] = {
                        'dfs_proxy': dfs_proxy.replace('/', '\\'),
                    }

    def load_gpo_list(self):
        """
        Load all GPO policies
        """

        result = check_output(['samba-tool', 'gpo', 'listall'], shell=False).decode().splitlines()
        for entry in result:
            if 'GPO' in entry:
                policy = entry.split(":")[-1].strip()
            elif 'display name' in entry:
                if entry.split(":")[-1].strip() == self.school:
                    self.policy = policy
                    break

    def load_drives(self):
        """
        Load Drives.xml content from school policies
        """

        xml_path = f'/var/lib/samba/sysvol/{samba_realm}/Policies/{self.policy}/User/Preferences/Drives/Drives.xml'
        self.Drives = Drives(self.policy)

    def get_share_prefix(self):

        if self.school in self.dfs.keys():
            self.share_prefix = self.dfs[self.school]['dfs_proxy']
        else:
            self.share_prefix = f'\\\\{samba_realm}\\{self.school}'

    def get_homepath(self, user, role, adminclass):

        if role == 'globaladministrator':
            home_path = f'\\\\{samba_realm}\\linuxmuster-global\\management\\{user}'
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
            'path' : f'\\\\{samba_realm}\\linuxmuster-global',
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
            ],
            'student': [
                home,
            ]
        }

        # Use GPO to determine if the share should be shown
        # Must be rewritten
        try:
            if not self.Drives.drives_dict['program']['disabled']:
                shares['teacher'].append(program)
                shares['student'].append(program)
        except KeyError:
            # Programs not in Drives.xml, ignoring
            pass
        try:
            if not self.Drives.drives_dict['share']['disabled']:
                shares['teacher'].append(share)
                shares['student'].append(share)
        except KeyError:
            # Shares not in Drives.xml, ignoring
            pass
        try:
            if not self.Drives.drives_dict['students']['disabled']:
                shares['teacher'].append(students)
        except KeyError:
            # Students-Home not in Drives.xml ?? Ignoring
            pass

        return shares[role]
