# -*- coding:utf8 -*-

import csv
from datetime import datetime
import os
import locale
import time
import subprocess
import gzip
import xml.etree.ElementTree as ET

LINBO_PATH = '/srv/linbo'

def read_config(group):
    """
    Get the os config from linbo config file start.conf.<group>

    :param group: Linbo group
    :type group: string
    :return: Config as list of dict
    :rtype: list of dict
    """

    path = os.path.join(LINBO_PATH, 'start.conf.'+group)
    osConfig = []
    if os.path.isfile(path):
        for line in open(path):
            line = line.split('#')[0].strip()

            if line.startswith('['):
                section = {}
                section_name = line.strip('[]')
                if section_name == 'OS':
                    osConfig.append(section)
            elif '=' in line:
                k, v = line.split('=', 1)
                v = v.strip()
                if v in ['yes', 'no']:
                    v = v == 'yes'
                section[k.strip()] = v
        return osConfig
    return None

def last_sync(workstation, image):
    """
    Get the date of the last sync date for a workstation w.

    :param w: Workstation
    :type w: string
    :param image: Name of the image file
    :type image: string
    :return: Last synchronisation time
    :rtype: datetime
    """

    statusfile = f'/var/log/linuxmuster/linbo/{workstation}_image.status'
    last = False

    if os.path.isfile(statusfile) and os.stat(statusfile).st_size != 0:
        for line in open(statusfile, 'r').readlines():
            if image in line:
                last = line.rstrip()
                break

    if last:
        ## Linbo locale is en_GB, not necessarily the server locale
        saved = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        last = datetime.strptime(last.split(' ')[0], '%Y%m%d%H%M')
        locale.setlocale(locale.LC_ALL, saved)

        last = time.mktime(last.timetuple())
    return last

def group_os(workstations):
    """
    Get all os infos from linbo config file and inject it in workstations dict.
    The workstations dict is set in the function list_workstations().

    :param workstations: Dict containing all workstations
    :type workstations: dict
    :return: Completed workstations dict with linbo informations
    :rtype: dict
    """

    for group in workstations.keys():
        workstations[group]['os'] = [] 
        config = read_config(group)
        if config is not None:
            workstations[group]['power'] = {
                'run_halt': 0,
                'timeout': 0
                }
            workstations[group]['auto'] = {
                'disable_gui': 0,
                'bypass': 0
            }
            for osConfig in config:
                if osConfig['SyncEnabled'] or osConfig['NewEnabled']:
                    tmpDict = {
                                'baseimage': osConfig['BaseImage'],
                                'partition': osConfig['Root'][-1],
                                'new_enabled': osConfig['NewEnabled'],
                                'start_enabled': osConfig['StartEnabled'],
                                'run_format': 0,
                                'run_sync':0,
                                'run_start':0,
                        }
                    workstations[group]['os'].append(tmpDict)

    return workstations

def list_workstations():
    """
    Generate a dict with workstations and parameters out of devices file

    :return: Dict with all linbo informations for all workstations.
    :rtype: dict
    """

    school = 'default-school'
    workstations_file = '/etc/linuxmuster/sophomorix/' + school + '/devices.csv'

    workstations = {}

    with open(workstations_file, 'r') as w:
        buffer = csv.reader(w, delimiter=";")
        for row in buffer:
            # Not a comment
            if row[0][0] != "#":
                # If config file exists
                if os.path.isfile(os.path.join(LINBO_PATH, 'start.conf.'+row[2])):
                    room = row[0]
                    group = row[2]
                    host  = row[1]
                    mac   = row[3]
                    ip    = row[4]
                    pxe   = row[10]

                    if pxe != "1" and pxe != "2":
                        continue
                    elif group not in workstations.keys():
                        workstations[group] = {'grp': group, 'hosts': [{'host' : host, 'room' : room, 'mac' : mac, 'ip' : ip}]}
                    else:
                        workstations[group]['hosts'].append({'host' : host, 'room' : room, 'mac' : mac, 'ip' : ip})

    return group_os(workstations)

def last_sync_all(workstations):
    """
    Add last synchronisation informations into the workstations dict,
    and status attribute to use as class for bootstrap.

    :param workstations: Dict of workstations set in list_workstations().
    :type workstations: dict
    :return: Completed dict of workstations
    :rtype: dict
    """

    today = time.mktime(datetime.now().timetuple())

    for group, grpDict in sorted(workstations.items()):
            for host in grpDict['hosts']:
                host['image'] = []
                for image in workstations[group]['os']:
                    last = last_sync(host['host'], image['baseimage'])
                    date = last if last else "Never"
                    tmpDict = {
                            'date': date,
                            'image': image['baseimage']
                    }
                    if date == "Never" or (today - date > 30*24*3600):
                        tmpDict['status'] = "danger"
                    elif today - date > 7*24*3600:
                        tmpDict['status'] = "warning"
                    else:
                        tmpDict['status'] = "success"
                    host['image'].append(tmpDict)


def test_online(host):
    """
    Launch a nmap on a host to test if the os is up, and return OS type.

    :param host: Hostname
    :type host: string
    :return: OS type (Off, Linbo, OS Linux, OS Windows, OS Unknown)
    :rtype: string
    """
    command=["nmap", "-p", "2222,22,135", host, "-oX", "-"]
    r = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False).stdout.read()
    xmlRoot = ET.fromstring(r)
    openPorts = []

    try:
        hostElement = xmlRoot.findall("host")[0]
        portsElement = hostElement.findall("ports")[0]
        scannedPorts = portsElement.findall("port")
    except:
        return get_os_from_open_ports([])

    for scannedPort in scannedPorts:
        portNumber = scannedPort.attrib["portid"]
        portState = scannedPort.findall("state")[0].attrib["state"]
        if portState == "open":
                openPorts.append(portNumber)

    return get_os_from_open_ports(openPorts)

def get_os_from_open_ports(openPorts):
    """
    Convert a list of open ports to an OS string.

    :param openPorts: The list of open ports
    :type openPorts: list
    :return: OS type (Off, Linbo, OS Linux, OS Windows, OS Unknown)
    :rtype: string
    """
    if len(openPorts) == 0:
            return "Off"
    elif len(openPorts) > 1:
            return "OS Unknown"

    if openPorts[0] == "22":
        return "OS Linux"
    elif openPorts[0] == "135":
        return "OS Windows"
    elif openPorts[0] == "2222":
        return "Linbo"
    else:
        return "OS Unknown"

def run(command):
    """
    Run linbo command.

    :param command: Linbo command
    :type command: list
    :return: Error as string if down, or 0 if successfull
    :rtype: string or integer
    """

    r = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False).stdout.read().decode()
    if 'Not online, host skipped.' in r:
        clients_error = ''
        for line in r.split('\n'):
            if 'Not online, host skipped.' in line:
                clients_error += line.split()[0] + ','

        return 'Not online, host skipped: ' + clients_error[:-1]
    else:
        return 0
