# -*- coding:utf8 -*-

import csv
from datetime import datetime
import os
import locale
import time
import subprocess
import xml.etree.ElementTree as ElementTree
from aj.plugins.lmn_common.lmnfile import LMNFile


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
                'timeout': 1
                }
            workstations[group]['auto'] = {
                'disable_gui': 0,
                'bypass': 0,
                'wol': 0,
                'prestart': 0,
                'partition': 0,
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

def list_workstations(context):
    """
    Generate a dict with workstations and parameters out of devices file

    :param context: user context set in views.py
    :return: Dict with all linbo informations for all workstations.
    :rtype: dict
    """

    path = f'{context.schoolmgr.configpath}devices.csv'
    school = context.schoolmgr.school
    devices_dict = {}
    fieldnames = [
        'room',
        'hostname',
        'group',
        'mac',
        'ip',
        'officeKey',
        'windowsKey',
        'dhcpOptions',
        'sophomorixRole',
        'lmnReserved10',
        'pxeFlag',
        'lmnReserved12',
        'lmnReserved13',
        'lmnReserved14',
        'sophomorixComment',
        'options',
    ]
    with LMNFile(path, 'r', fieldnames=fieldnames) as devices_csv:

        devices = devices_csv.read()
        for device in devices:
            if school != 'default-school':
                if device['hostname']:
                    device['hostname'] = f'{school}-{device["hostname"]}'
            if os.path.isfile(os.path.join(LINBO_PATH, 'start.conf.'+str(device['group']))):
                if device['pxeFlag'] != '1' and device['pxeFlag'] != "2":
                    continue
                elif device['group'] not in devices_dict.keys():
                    devices_dict[device['group']] = {'grp': device['group'], 'hosts': [device]}
                else:
                    devices_dict[device['group']]['hosts'].append(device)
    return group_os(devices_dict)

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
                    last = last_sync(host['hostname'], image['baseimage'])
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
    xmlRoot = ElementTree.fromstring(r)

    numberOfOnlineHosts = int(xmlRoot.find("runstats").find("hosts").attrib["up"])
    if numberOfOnlineHosts == 0:
        return "Off"

    ports = {}
    scannedPorts = xmlRoot.find("host").find("ports").findall("port")

    for scannedPort in scannedPorts:
        portNumber = scannedPort.attrib["portid"]
        portState = scannedPort.find("state").attrib["state"]
        ports[portNumber] = portState

    return get_os_from_ports(ports)

def get_os_from_ports(ports):
    """
    Convert a dict of ports to an OS string.

    :param openPorts: The dict of open ports (key: port number, value: port state)
    :type openPorts: dict
    :return: OS type (Linbo, OS Linux, OS Windows, OS Unknown)
    :rtype: string
    """

    if is_port_signature_linbo(ports):
        return "Linbo"
    if is_port_signature_linux(ports):
        return "OS Linux"
    if is_port_signature_windows(ports):
        return "OS Windows"
    return "OS Unknown"

def is_port_signature_linbo(ports):
    """
    Check if a dict of ports belongs to a Linbo host.
    The criteria for Linbo is, that ONLY port 2222 is open
    
    :param openPorts: The dict of open ports (key: port number, value: port state)
    :type openPorts: dict
    :return: Whether it's a Linbo host
    :rtype: bool
    """

    openPortNumbers = []
    for port in ports:
        if ports[port] == "open":
            openPortNumbers.append(port)

    return (
        "2222" in openPortNumbers 
        and len(openPortNumbers) == 1
    )

def is_port_signature_linux(ports):
    """
    Check if a dict of ports belongs to a Linux host.
    The criteria for Linux is, that port 22 is open and 135 is closed.
    
    :param openPorts: The dict of open ports (key: port number, value: port state)
    :type openPorts: dict
    :return: Whether it's a Linux host
    :rtype: bool
    """

    return (
        "22" in ports
        and ports["22"] in ["open", "filtered"]
        and (
            "135" not in ports
            or ports["135"] != "open"
        )
    )

def is_port_signature_windows(ports):
    """
    Check if a dict of ports belongs to a Windows host.
    The criteria for Windows is, that port 135 is open and 22 is not open.
    
    :param openPorts: The dict of open ports (key: port number, value: port state)
    :type openPorts: dict
    :return: Whether it's a Windows host
    :rtype: bool
    """

    return (
        "135" in ports
        and ports["135"] in ["open", "filtered"]
        and (
            "22" not in ports
            or ports["22"] != "open"
        )
    )

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
