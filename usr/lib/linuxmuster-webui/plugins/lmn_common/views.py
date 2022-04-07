"""
Common tools to manipulate user's files and config files on the OS.
"""

import os
import shutil
import difflib
import re
import pwd, grp
import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.lmn_common.lmnfile import LMNFile


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    ## TODO authorize
    ## Used in lmn_common/resources/js/directives.coffee:22
    @url(r'/api/lm/log(?P<path>.+)')
    @endpoint(api=True)
    def handle_api_log(self, http_context, path=None):
        """
        Query a part of a log file to simulate a continuously flow on the
        frontend.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of the log file
        :type path: string
        :return: Part of the log at offset `offset`
        :rtype: string
        """

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
        """
        Create directory with given path, ignoring errors.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: True if success
        :rtype: bool or None
        """

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
        """
        Remove directory and its content with given path, ignoring errors.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: True if success
        :rtype: bool or None
        """

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
        """
        Remove file with given path.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: True if success
        :rtype: bool or None
        """

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
        """
        Chown file with given path, owner and group.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: True if success
        :rtype: bool or None
        """

        if http_context.method == 'POST':
            # school = 'default-school'
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
        """
        Read linuxmuster setup file for linbo and setup wizard.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Config content
        :rtype: dict
        """

        try:
            path = '/var/lib/linuxmuster/setup.ini'
            if http_context.method == 'GET':
                with LMNFile(path, 'r') as setup:
                    return setup.data
        except FileNotFoundError:
            return

    # TODO authorize
    @url(r'/api/lm/diff')
    @endpoint(api=True)
    def handle_api_diff(selfself, http_context):

        if http_context.method == 'POST':
            file1 = http_context.json_body()['file1']
            file2 = http_context.json_body()['file2']

            with open(file1) as f:
                fromlines = f.readlines()

            with open(file2) as f:
                tolines = f.readlines()

            diff = difflib.unified_diff(fromlines, tolines, file1, file2, n=0)

            # Some formatting
            def format_diff(entry):
                entry = re.sub(r'^---', r'<<<', entry)
                entry = re.sub(r'^\+\+\+', r'>>>', entry)
                entry = re.sub(r'^-', r'< ', entry)
                entry = re.sub(r'^\+', r'> ', entry)
                return entry.strip()

            return [format_diff(entry) for entry in diff]

    ## TODO authorize
    ## Used in
    @url(r'/api/lm/version')
    @endpoint(api=True)
    def handle_api_version(self, http_context):
        """
        Get the versions of the installed LMN packages using dpkg.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of packages with informations
        :rtype: dict
        """

        if http_context.method == 'GET':
            packages = subprocess.check_output("dpkg -l | grep linuxmuster- | awk 'BEGIN {OFS=\"=\";} {print $2,$3}'", shell=True).decode().split()
            return dict([package.split('=') for package in packages])


    ## NOT USED YET
    # @url(r'/api/lm/all-users') ## TODO authorize
    # @endpoint(api=True)
    # def handle_api_get_userdetails(self, http_context):
        # if http_context.method == 'POST':
            # sophomorixCommand = ['sophomorix-query', '--student', '--teacher', '--schooladministrator', '--globaladministrator', '-jj']
            # all_users = lmn_getSophomorixValue(sophomorixCommand, 'USER')
            # return all_users

    @url(r'/api/lmn/activeschool')
    @endpoint(api=True)
    def handle_get_activeSchool(self, http_context):
        """
        Get  activeSchool.
        Method GET: gets active school

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: String containing active school
        :rtype: string 
        """
        if http_context.method == 'GET':
            return self.context.schoolmgr.school
