#!/usr/bin/python3
import subprocess

print("* Create Webui Configuration")

subprocess.run(['/usr/lib/linuxmuster-webui/etc/install_scripts/create_aj_cfg.sh'])

print("* Create Webui Upload Folder")
subprocess.run(['/usr/lib/linuxmuster-webui/etc/install_scripts/create_webuiUploadFolder.sh'])

print("* Create Webui Installed Flag")
subprocess.run(['touch', '/usr/lib/linuxmuster-webui/etc/.installed'])

print("* WebUI Setup Success!")
