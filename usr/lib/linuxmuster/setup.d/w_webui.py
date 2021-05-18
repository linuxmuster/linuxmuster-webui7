#!/usr/bin/python3
import subprocess

print("* Create Webui Configuration")

subprocess.run(['/usr/lib/linuxmuster-webui/etc/create_aj_cfg.sh'])

print("* Create Webui Upload Folder")
subprocess.run(['/usr/lib/linuxmuster-webui/etc/create_webuiUploadFolder.sh'])

print("* WebUI Setup Success!")
