#!/usr/bin/python3
#
# final tasks
# thomas@linuxmuster.net
# 20170212
#

import os
import sys
import subprocess

# import devices
msg = 'Setting Webui-Permissions'
try:
    subprocess.call("/usr/lib/linuxmuster-webui/plugins/lm_setup_wizard/template.sh", shell=True)

except:
    printScript(' Failed!', '', True, True, False, len(msg))
    sys.exit(1)
