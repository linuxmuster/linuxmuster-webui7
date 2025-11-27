#!/usr/bin/python3
import subprocess

print("* Create Webui Configuration")

subprocess.run(['/usr/lib/linuxmuster-webui/etc/install_scripts/create_aj_cfg.sh'])

print("* WebUI Setup Success!")
