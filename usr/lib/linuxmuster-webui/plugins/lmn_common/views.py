import os
import shutil
import pwd, grp

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.lmn_common.api import lmn_getSophomorixValue, check_allowed_path

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    ## TODO authorize
    ## Used in lmn_common/resources/js/directives.coffee:22
    @url(r'/api/lm/log(?P<path>.+)')
    @endpoint(api=True)
    def handle_api_log(self, http_context, path=None):
        if not os.path.exists(path):
            return ''
        with open(path) as f:
            f.seek(int(http_context.query.get('offset', '0')))
            return f.read()

    ## TODO authorize
    ## Used in lmn_session/resources/js/controllers/session.controller.coffee:76
    @url(r'/api/lm/create-dir')
    @endpoint(api=True)
    def handle_api_create_dir(self, http_context):
        """Create directory with given path, ignoring errors"""
        if http_context.method == 'POST':
            filepath = http_context.json_body()['filepath']
            if not os.path.exists(filepath):
                os.makedirs(filepath)
                return True
            return

    ## TODO authorize
    ## Used in lmn_session/resources/js/controllers/session.controller.coffee:76
    @url(r'/api/lm/remove-dir')
    @endpoint(api=True)
    def handle_api_remove_dir(self, http_context):
        """Remove directory and its content with given path, ignoring errors"""
        if http_context.method == 'POST':
            filepath = http_context.json_body()['filepath']
            if not os.path.exists(filepath):
                return
            shutil.rmtree(filepath, ignore_errors=True)
            return True

    ## TODO authorize
    ## Used in directive upload, lmFileBackups and lmn_session/resources/js/controllers/session.controller.coffee:60
    @url(r'/api/lm/remove-file') ## TODO authorize
    @endpoint(api=True)
    def handle_api_remove_file(self, http_context):
        """Remove file with given path"""
        if http_context.method == 'POST':
            filepath = http_context.json_body()['filepath']
            if not os.path.exists(filepath):
                return
            os.unlink(filepath)
            return True

    ## NOT USED YET
    # @url(r'/api/lm/remove-backup') ## TODO authorize
    # @endpoint(api=True)
    # def handle_api_remove_backup(self, http_context):
        # """Remove backup file in directory /etc/linuxmuster/sophomorix/SCHOOL"""
        # if http_context.method == 'POST':
            # backup_path = http_context.json_body()['filepath']
            # school = 'default-school'
            # filepath = '/etc/linuxmuster/sophomorix/' + school + '/' + backup_path
            # if not os.path.exists(filepath):
                # return
            # # Do not allow to navigate
            # elif '..' in backup_path:
                # return
            # else:
                # os.unlink(filepath)
                # return True

    ## TODO authorize
    ## Used in directive upload
    @url(r'/api/lm/chown') ## TODO authorize
    @endpoint(api=True)
    def handle_api_chown(self, http_context):
        """Chown file with given path, owner and group."""
        if http_context.method == 'POST':
            school = 'default-school'
            filepath = http_context.json_body()['filepath']
            owner = http_context.json_body()['owner']
            group = http_context.json_body()['group']
            if not os.path.exists(filepath):
                return
            try:
                user_id  = pwd.getpwnam(owner).pw_uid
                group_id = grp.getgrnam(group).gr_gid
                os.chown(filepath, user_id, group_id)
                return True
            except:
                return

    ## TODO authorize : authorize possible with setup_wizard ?
    @url(r'/api/lm/read-config-setup')
    @endpoint(api=True)
    def handle_api_read_setup_ini(self, http_context):
        path = '/var/lib/linuxmuster/setup.ini'
        if http_context.method == 'GET':
            config = {}
            for line in open(path, 'rb'):
                line = line.decode('utf-8', errors='ignore')
                line = line.split('#')[0].strip()

                if line.startswith('['):
                    section = {}
                    section_name = line.strip('[]')
                    if section_name == 'setup':
                        config['setup'] = section
                elif '=' in line:
                    k, v = line.split('=', 1)
                    v = v.strip()
                    section[k.strip()] = v
            return config

    ## NOT USED YET
    # @url(r'/api/lm/all-users') ## TODO authorize
    # @endpoint(api=True)
    # def handle_api_get_userdetails(self, http_context):
        # if http_context.method == 'POST':
            # sophomorixCommand = ['sophomorix-query', '--student', '--teacher', '--schooladministrator', '--globaladministrator', '-jj']
            # all_users = lmn_getSophomorixValue(sophomorixCommand, 'USER')
            # return all_users
