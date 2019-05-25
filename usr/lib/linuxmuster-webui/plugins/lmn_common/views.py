import os
import shutil

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.lmn_common.api import lmn_getSophomorixValue

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/log(?P<path>.+)')
    @endpoint(api=True)
    def handle_api_log(self, http_context, path=None):
        if not os.path.exists(path):
            return ''
        with open(path) as f:
            f.seek(int(http_context.query.get('offset', '0')))
            return f.read()
    
    @url(r'/api/lm/remove-dir') ## TODO authorize
    @endpoint(api=True)
    def handle_api_remove_dir(self, http_context):
        """Remove directory and its content with given path, ignoring errors"""
        if http_context.method == 'POST':
            filepath = http_context.json_body()['filepath']
            if not os.path.exists(filepath):
                return
            else:
                shutil.rmtree(filepath, ignore_errors=True)
                return True
    
    @url(r'/api/lm/remove-file') ## TODO authorize
    @endpoint(api=True)
    def handle_api_remove_file(self, http_context):
        """Remove file with given path"""
        if http_context.method == 'POST':
            filepath = http_context.json_body()['filepath']
            if not os.path.exists(filepath):
                return
            else:
                os.unlink(filepath)
                return True
        
    @url(r'/api/lm/remove-backup') ## TODO authorize
    @endpoint(api=True)
    def handle_api_remove_backup(self, http_context):
        """Remove backup file in directory /etc/linuxmuster/sophomorix/SCHOOL"""
        if http_context.method == 'POST':
            school = 'default-school'
            filepath = '/etc/linuxmuster/sophomorix/' + school + '/' + http_context.json_body()['filepath']
            if not os.path.exists(filepath):
                return
            else:
                os.unlink(filepath)
                return True
                
    @url(r'/api/lm/read-config-setup') ## TODO authorize
    @endpoint(api=True)
    def handle_api_read_setup_ini(self, http_context):
        path = '/var/lib/linuxmuster/setup.ini'
        if http_context.method == 'GET':
            config = {}
            for line in open(path):
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
                
    @url(r'/api/lm/all-users') ## TODO authorize
    @endpoint(api=True)
    def handle_api_get_userdetails(self, http_context):
        if http_context.method == 'POST':
            sophomorixCommand = ['sophomorix-query', '--student', '--teacher', '--schooladministrator', '--globaladministrator', '-jj']
            all_users = lmn_getSophomorixValue(sophomorixCommand, 'USER')
            return all_users
