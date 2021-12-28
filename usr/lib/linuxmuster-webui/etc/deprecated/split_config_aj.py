#!/usr/bin/python3

import yaml
import shutil
import os
import sys

path_ajenti  = '/etc/ajenti/'
path_webui   = '/etc/linuxmuster/webui/'
config_file  = 'config.yml'
config_webui = {}

if not os.path.isfile(path_webui + config_file):
    try:
        if not os.path.isdir(path_webui):
            os.mkdir(path_webui, 755)
            ## Backup
            shutil.copyfile(path_ajenti + config_file, path_ajenti + config_file + '.bak')

            ## Load existing config
            print("Load existing ajenti config file ...")
            with open(path_ajenti + config_file, 'r') as f:
                config_ajenti = yaml.load(f, Loader=yaml.Loader)
    except:
        print("Error loading ajenti config file ...")
        sys.exit()

    ## Copy linuxmuster config
    print("Copy linuxmuster config in /etc/linuxmuster/webui/config.yml ...")
    try:
        config_webui['linuxmuster'] = config_ajenti['linuxmuster']
        ## Update ajenti config
        print("Update ajenti config ...")
        del config_ajenti['linuxmuster']
    except:
        print("Linuxmuster key not found ! Please check the file /etc/linuxmuster/webui/config.yml !")

    with open(path_webui + config_file, 'w') as f:
        yaml.dump(config_webui, f, default_flow_style=False)

    with open(path_ajenti + config_file, 'w') as f:
        yaml.dump(config_ajenti, f, default_flow_style=False)

    print("Finished!")
else:
    print("Config files for WebUI are already ok!")
