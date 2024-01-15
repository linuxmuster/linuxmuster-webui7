"""
Common tools to communicate with sophomorix and handle config files.
"""

import os
import subprocess
import dpath.util
import re
import threading
import ast
import logging
from pprint import pformat
from .lmnfile import LMNFile
from configparser import ConfigParser
from time import time

# Load Webui settings
config_path = '/etc/linuxmuster/webui/config.yml'
if os.path.isfile(config_path):
    with LMNFile(config_path, 'r') as webui:
        lmconfig = webui.read()

        # LDAP config for auth
        ldap_config = lmconfig['linuxmuster']['ldap']

        # Password reset configuration for restricted worker
        pwreset_config = lmconfig['linuxmuster'].get('pw_reset', {})
        pwreset_config['activate'] = pwreset_config.get('activate', False)
        pwreset_config['ldap_mail_field'] = pwreset_config.get('ldap_mail_field', False)

        # Samba config to eventually override the share prefix
        samba_override = lmconfig['linuxmuster'].get('samba', {})
        samba_override['share_prefix'] = samba_override.get('share_prefix', '')

        # Display options
        display_options = lmconfig['linuxmuster'].get('display', {})
        display_options['show_webdav'] = display_options.get('show_webdav', True)
else:
    lmconfig = {}
    ldap_config = {}
    pwreset_config = {}
    samba_override = {}
    display_options = {}
    logging.error("Without config.yml the users will not be able to login.")

# Load samba domain
smbconf = ConfigParser()
try:
    smbconf.read('/etc/samba/smb.conf')
    samba_realm = smbconf["global"]["realm"].lower()
    samba_workgroup = smbconf["global"]["workgroup"]
    samba_netbios = smbconf["global"]["netbios name"].lower()
    samba_domain = f'{samba_netbios}.{samba_realm}'
except Exception:
    logging.error("Can not read realm and domain from smb.conf")
    samba_domain, samba_realm, samba_netbios, samba_workgroup = ['']*4

# Fix missing entries in the lmconfig. Should be later refactored
# and the config file should be splitted
# Main linuxmuster config entry
lmconfig.setdefault('linuxmuster', {})
lmconfig['linuxmuster'].setdefault('ldap', {})
# Templates for password printing
lmconfig.setdefault('passwordTemplates', {})

# Used for pageTitle, see lmn_auth.api
try:
    with LMNFile('/var/lib/linuxmuster/setup.ini', 'r') as s:
        try:
            lmsetup_schoolname = s.data['setup']['schoolname']
        except KeyError:
            lmsetup_schoolname = None
except FileNotFoundError:
    lmsetup_schoolname = None

class SophomorixProcess(threading.Thread):
    """
    Worker for processing sophomorix commands.
    """

    def __init__(self, command, sensitive):
        self.stdout = None
        self.stderr = None
        self.command = command
        self.sensitive = sensitive
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, sensitive=self.sensitive)
        self.stdout, self.stderr = p.communicate()


def lmn_getSophomorixValue(sophomorixCommand, jsonpath, ignoreErrors=False, sensitive=False):
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
    s = time()
    t = SophomorixProcess(sophomorixCommand, sensitive=sensitive)
    t.daemon = True
    t.start()
    t.join()
    logging.debug(f"Sophomorix command time : {time()-s}")

    # Cleanup stderr output
    # output = t.stderr.replace(':null,', ":\"null\",")
    # TODO: Maybe sophomorix should provide the null value  in  a python usable format
    s = time()
    output = t.stderr.decode("utf8").replace(':null', ":\"null\"")
    output = output.replace(':null}', ":\"null\"}")
    output = output.replace(':null]', ":\"null\"]")


    # Some comands get many dicts, we just want the first
    output = output.replace('\n', '').split('# JSON-end')[0]
    output = output.split('# JSON-begin')[1]
    output = re.sub('# JSON-begin', '', output)
    logging.debug(f"Sophomorix filter result time : {time()-s}")

    # Convert str to dict
    jsonDict = {}
    if output:
        s = time()
        jsonDict = ast.literal_eval(output)
        logging.debug(f"Sophomorix convert to dict time : {time()-s}")

    if debug:
        logging.debug(
            f"Sophomorix stdout :\n {t.stdout.decode('utf-8')}"
            f"Sophomorix sdterr :\n {pformat(jsonDict)}"
        )

    # Without key, simply return the dict
    if jsonpath == '':
        return jsonDict

    if ignoreErrors is False:
        try:
            s = time()
            resultString = dpath.util.get(jsonDict, jsonpath)
            logging.debug(f"Sophomorix search in dict time : {time()-s}")
        except Exception as e:
            raise Exception(
                'Sophomorix Value error !\n\n'
                f'Either sophomorix field does not exist or user does not have sufficient permissions:\n'
                f'Error Message: {e}\n'
                f'Dictionary we looked for information:\n'
                f'{jsonDict}'
            )
    else:
        resultString = dpath.util.get(jsonDict, jsonpath)
    return resultString

