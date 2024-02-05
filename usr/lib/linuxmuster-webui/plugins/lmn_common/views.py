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
from aj.api.http import get, post, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.lmn_common.lmnfile import LMNFile
from aj.plugins.lmn_common.api import display_options


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    ## TODO authorize
    ## Used in lmn_common/resources/js/directives.coffee:22
    @get(r'/api/lmn/log(?P<path>.+)')
    @endpoint(api=True)
    def handle_api_log(self, http_context, path=None):
        """
        Query a part of a log file to simulate a continuously flow on the
        frontend.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of the log file
        :type path: string
        :return: Part of the log at offset `offset`
        :rtype: string
        """

        if os.getuid() != 0:
            http_context.respond_forbidden()
            return ''

        if not os.path.exists(path):
            http_context.respond_not_found()
            return ''

        with open(path) as f:
            f.seek(int(http_context.query.get('offset', '0')))
            return f.read()

    ## DEPRECATED
    ## Used in lmn_session/resources/js/controllers/session.controller.coffee:76
    # @post(r'/api/lmn/create-dir')
    # @endpoint(api=True)
    # def handle_api_create_dir(self, http_context):
    #     """
    #     Create directory with given path, ignoring errors.
    #
    #     :param http_context: HttpContext
    #     :type http_context: HttpContext
    #     :return: True if success
    #     :rtype: bool or None
    #     """
    #
    #     filepath = http_context.json_body()['filepath']
    #     if not os.path.exists(filepath):
    #         os.makedirs(filepath)
    #         return True
    #     return

    ## DEPRECATED
    # ## Used in lmn_session/resources/js/controllers/session.controller.coffee:76
    # @post(r'/api/lmn/remove-dir')
    # @endpoint(api=True)
    # def handle_api_remove_dir(self, http_context):
    #     """
    #     Remove directory and its content with given path, ignoring errors.
    #
    #     :param http_context: HttpContext
    #     :type http_context: HttpContext
    #     :return: True if success
    #     :rtype: bool or None
    #     """
    #
    #     filepath = http_context.json_body()['filepath']
    #     if not os.path.exists(filepath):
    #         return
    #     shutil.rmtree(filepath, ignore_errors=True)
    #     return True

    ## TODO authorize
    ## Used in directive upload, lmFileBackups and lmn_session/resources/js/controllers/session.controller.coffee:60
    @post(r'/api/lmn/remove-file')
    @endpoint(api=True)
    def handle_api_remove_file(self, http_context):
        """
        Remove file with given path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: True if success
        :rtype: bool or None
        """

        if os.getuid() != 0:
            http_context.respond_forbidden()
            return ''

        filepath = http_context.json_body()['filepath']
        if not os.path.exists(filepath):
            http_context.respond_not_found()
            return ''

        os.unlink(filepath)
        return True

    ## DEPRECATED
    ## Used in directive upload
    # @post(r'/api/lmn/chown')
    # @endpoint(api=True)
    # def handle_api_chown(self, http_context):
    #     """
    #     Chown file with given path, owner and group.
    #
    #     :param http_context: HttpContext
    #     :type http_context: HttpContext
    #     :return: True if success
    #     :rtype: bool or None
    #     """
    #
    #     filepath = http_context.json_body()['filepath']
    #     owner = http_context.json_body()['owner']
    #     group = http_context.json_body()['group']
    #     if not os.path.exists(filepath):
    #         return
    #     try:
    #         user_id  = pwd.getpwnam(owner).pw_uid
    #         group_id = grp.getgrnam(group).gr_gid
    #         os.chown(filepath, user_id, group_id)
    #         return True
    #     except:
    #         return

    ## TODO authorize : authorize possible with setup_wizard ?
    @get(r'/api/lmn/read-config-setup')
    @endpoint(api=True)
    def handle_api_read_setup_ini(self, http_context):
        """
        Read linuxmuster setup file for linbo and setup wizard.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Config content
        :rtype: dict
        """

        if os.getuid() != 0:
            http_context.respond_forbidden()
            return ''
        
        try:
            path = '/var/lib/linuxmuster/setup.ini'
            with LMNFile(path, 'r') as setup:
                return setup.data
        except FileNotFoundError:
            return

    # TODO authorize
    @post(r'/api/lmn/diff')
    @endpoint(api=True)
    def handle_api_diff(self, http_context):
        """
        Check differences between two files.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Lines that differ
        :rtype: list
        """

        if os.getuid() != 0:
            http_context.respond_forbiddent()
            return ''

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
    @get(r'/api/lmn/version')
    @endpoint(api=True)
    def handle_api_version(self, http_context):
        """
        Get the versions of the installed LMN packages using dpkg.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of packages with informations
        :rtype: dict
        """

        packages = subprocess.check_output("dpkg -l | grep linuxmuster- | awk 'BEGIN {OFS=\"=\";} {print $2,$3}'", shell=True).decode().split()
        return dict([package.split('=') for package in packages])

    @get(r'/api/lmn/activeschool')
    @endpoint(api=True)
    def handle_get_activeSchool(self, http_context):
        """
        Get  activeSchool.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: String containing active school
        :rtype: string 
        """

        return self.context.schoolmgr.school

    @get(r'/api/lmn/display_options')
    @endpoint(api=True)
    def handle_get_display_options(self, http_context):
        """
        Provide display options stored in the webui config file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: display options
        :rtype: dict
        """

        return display_options
