"""
Common tools to communicate with sophomorix and handle config files.
"""

import os
import time
import subprocess
import dpath.util
import re
import yaml
import threading
import ast
import unicodecsv as csv
import filecmp
import configparser
import logging
from pprint import pformat
from .lmnfile import LMNFile


ALLOWED_PATHS = [
                '/etc/linuxmuster/sophomorix/',     # used for school.conf or *.csv in lmn_settings, lmn_devices and lmn_users
                '/srv/linbo',                       # used in lmn_linbo for start.conf
                '/etc/linuxmuster/subnets-dev.csv'  # used in lmn_settings for subnets configuration
                ]

def check_allowed_path(path):
    """
    Check path before modifying files for security reasons.

    :param path: File to modify
    :type path: string
    :return: File path in allowed paths.
    :rtype: bool
    """

    allowed_path = False
    for rootpath in ALLOWED_PATHS:
        if rootpath in path:
            allowed_path = True
            break

    if allowed_path and '..' not in path:
        return True
    raise IOError(_("Access refused."))  # skipcq: PYL-E0602

# Load Webui settings
with LMNFile('/etc/linuxmuster/webui/config.yml', 'r') as webui:
    lmconfig = webui.read()

# Used for pageTitle, see lmn_auth.api
try:
    with LMNFile('/var/lib/linuxmuster/setup.ini', 'r') as s:
        try:
            lmsetup_schoolname = s.data['setup']['schoolname']
        except KeyError:
            lmsetup_schoolname = None
except FileNotFoundError:
    lmsetup_schoolname = None


def lmn_get_school_configpath(school):
    """
    Return the default absolute path for config files in multischool env.

    :param school: school shortname

    """
    if school == "default-school":
        return '/etc/linuxmuster/sophomorix/default-school/'
    else:
        return '/etc/linuxmuster/sophomorix/'+school+'/'+school+'.'

class SophomorixProcess(threading.Thread):
    """
    Worker for processing sophomorix commands.
    """

    def __init__(self, command):
        self.stdout = None
        self.stderr = None
        self.command = command
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        self.stdout, self.stderr = p.communicate()


def lmn_getSophomorixValue(sophomorixCommand, jsonpath, ignoreErrors=False):
    """
    Connector to all sophomorix commands. Run a sophomorix command with -j
    option (output as json) through a SophomorixProcess and parse the results.

    :param sophomorixCommand: Command with options to run
    :type sophomorixCommand: list
    :param jsonpath: Key to search in the resulted dict, e.g. /USERS/doe
    :type jsonpath: string
    :param ignoreErrors: Quiet mode
    :type ignoreErrors: bool
    :return: Whole output or key if jsonpath is defined
    :rtype: dict or value (list, dict, integer, string)
    """

    debug = lmconfig['linuxmuster'].get("sophomorix-debug", False)

    uid = os.getuid()
    if uid != 0:
        sophomorixCommand = ['sudo'] + sophomorixCommand

    # New Thread for one process to avoid conflicts
    t = SophomorixProcess(sophomorixCommand)
    t.daemon = True
    t.start()
    t.join()

    # Cleanup stderr output
    # output = t.stderr.replace(':null,', ":\"null\",")
    # TODO: Maybe sophomorix should provide the null value  in  a python usable format
    output = t.stderr.decode("utf8").replace(':null', ":\"null\"")
    output = output.replace(':null}', ":\"null\"}")
    output = output.replace(':null]', ":\"null\"]")


    # Some comands get many dicts, we just want the first
    output = output.replace('\n', '').split('# JSON-end')[0]
    output = output.split('# JSON-begin')[1]
    output = re.sub('# JSON-begin', '', output)

    # Convert str to dict
    jsonDict = {}
    if output:
        jsonDict = ast.literal_eval(output)

    if debug:
        logging.debug("Sophomorix stdout :\n %s", t.stdout.decode('utf-8'))
        logging.debug("Sophomorix sdterr :\n %s", pformat(jsonDict))

    # Without key, simply return the dict
    if jsonpath is '':
        return jsonDict

    if ignoreErrors is False:
        try:
            resultString = dpath.util.get(jsonDict, jsonpath)
        except Exception as e:
            raise Exception('getSophomorix Value error. Either sophomorix field does not exist or ajenti binduser does not have sufficient permissions:\n' +
                            'Error Message: ' + str(e) + '\n Dictionary we looked for information:\n' + str(jsonDict))
    else:
        resultString = dpath.util.get(jsonDict, jsonpath)
    return resultString

