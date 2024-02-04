from jadi import component

from aj.auth import authorize
from aj.api.http import post, get, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.lmnfile import LMNFile

import os
import nmap
import subprocess
import locale
import time

from datetime import datetime


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @post(r'/api/lmn/device-manager/getdevices')
    @authorize('lm:device-manager:read')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_getdevices(self, http_context):
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
        filepath = http_context.json_body()['filepath']
        school = http_context.json_body()['school']
        allowedTypes = ["addc", "server", "classroom-studentcomputer",
                        "classroom-teachercomputer", "staffcomputer", "faculty-teachercomputer"]

        with LMNFile(filepath, 'r', fieldnames=fieldnames) as devices:
            returnArray = []
            for host in devices.read():
                if '#' not in host['room'] and host["hostname"] != None and host["mac"] != None and host["sophomorixRole"] in allowedTypes:
                    if host["sophomorixRole"] == "addc" or host["sophomorixRole"] == "server":
                        remoteBlock = True
                    else:
                        remoteBlock = False

                    returnArray.append({
                        'room': host['room'],
                        'hostname': host['hostname'],
                        'group': host['group'],
                        'mac': host['mac'],
                        'ip': host['ip'],
                        'type': host['sophomorixRole'],
                        'os': 'Unknown',
                        'online': 'Unknown',
                        'checked': False,
                        'remoteBlock': remoteBlock,
                        'school': school
                    })
        return returnArray

    @post(r'/api/lmn/device-manager/checkOnline')
    @authorize('lm:device-manager:read')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_checkOnline(self, http_context):
        device = http_context.json_body()['device']
        nmScan = nmap.PortScanner()
        scanResult = nmScan.scan(hosts=device["ip"], arguments='-n -sP')
        if device["ip"] in scanResult["scan"]:
            return scanResult["scan"][device["ip"]]["status"]["state"]
        return "down"

    @post(r'/api/lmn/device-manager/checkOS')
    @authorize('lm:device-manager:read')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_checkOS(self, http_context):
        device = http_context.json_body()['device']
        nmScan = nmap.PortScanner()
        scanResult = nmScan.scan(
            device["ip"], "22,135,2222", arguments='-n')
        if device["ip"] in scanResult["scan"]:
            if scanResult["scan"][device["ip"]]["tcp"][22]["state"] == "open":
                return "Linux"
            if scanResult["scan"][device["ip"]]["tcp"][135]["state"] == "open":
                return "Windows"
            if scanResult["scan"][device["ip"]]["tcp"][2222]["state"] == "open":
                return "Linbo"
        return "Unknown"

    @post(r'/api/lmn/device-manager/shutdown')
    @authorize('lm:device-manager:modify')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_shutdown(self, http_context):
        device = http_context.json_body()['device']
        if device["os"] == "Linbo":
            command = ["linbo-remote", "-s", device["school"],
                       "-i", device["hostname"], "-c", "halt"]

        elif device["os"] == "Linux":
            command = ["ssh", device["hostname"], "-l", "root", "'init 0'"]

        elif device["os"] == "Windows":
            command = ["net", "rpc", "-S", device["hostname"], "-U",
                       "administrator%$(cat /etc/linuxmuster/.secret/administrator)", "shutdown", "-t", "1", "-f"]

        else:
            return {"status": False, "exitcode": None, "message": "Could not determine os!"}

        r = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        result = r.stdout.read().decode("utf-8")
        (err, out) = r.communicate()
        if r.returncode == 0:
            return {"status": True, "exitcode": r.returncode, "message": result}
        return {"status": False, "exitcode": r.returncode, "message": result}

    @post(r'/api/lmn/device-manager/reboot')
    @authorize('lm:device-manager:modify')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_reboot(self, http_context):
        device = http_context.json_body()['device']
        if device["os"] == "Linbo":
            command = ["linbo-remote", "-s", device["school"],
                       "-i", device["hostname"], "-c", "reboot"]

        elif device["os"] == "Linux":
            command = ["ssh", device["hostname"], "-l", "root", "'init 6'"]

        elif device["os"] == "Windows":
            command = ["net", "rpc", "-S", device["hostname"], "-U",
                       "administrator%$(cat /etc/linuxmuster/.secret/administrator)", "shutdown", "-r", "-t", "1", "-f"]

        else:
            return {"status": False, "exitcode": None, "message": "Could not determine os!"}

        r = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        result = r.stdout.read().decode("utf-8")
        (err, out) = r.communicate()
        if r.returncode == 0:
            return {"status": True, "exitcode": r.returncode, "message": result}
        return {"status": False, "exitcode": r.returncode, "message": result}

    @post(r'/api/lmn/device-manager/start')
    @authorize('lm:device-manager:modify')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_start(self, http_context):
        device = http_context.json_body()['device']
        command = ["linbo-remote", "-s", device["school"],
                   "-i", device["hostname"], "-w", "0"]
        r = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        result = r.stdout.read().decode("utf-8")
        (err, out) = r.communicate()
        if r.returncode == 0:
            return {"status": True, "exitcode": r.returncode, "message": result}
        return {"status": False, "exitcode": r.returncode, "message": result}

    @post(r'/api/lmn/device-manager/run')
    @authorize('lm:device-manager:modify')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_run(self, http_context):
        command = http_context.json_body()['command']
        command = command.split(" ")
        r = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        result = r.stdout.read().decode("utf-8")
        (err, out) = r.communicate()
        if r.returncode == 0:
            return {"status": True, "exitcode": r.returncode, "message": result}
        return {"status": False, "exitcode": r.returncode, "message": result}

    @post(r'/api/lmn/device-manager/getlinboconfig')
    @authorize('lm:device-manager:read')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_getlinboconfig(self, http_context):
        device = http_context.json_body()['device']
        path = os.path.join("/srv/linbo", 'start.conf.' + device["group"])
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

    @post(r'/api/lmn/device-manager/getlastsync')
    @authorize('lm:device-manager:read')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_getlastsync(self, http_context):
        device = http_context.json_body()['device']
        image = http_context.json_body()['image']
        statusfile = "/var/log/linuxmuster/linbo/" + \
            device["hostname"] + "_image.status"
        last = False
        last_tupln = False

        if os.path.isfile(statusfile) and os.stat(statusfile).st_size != 0:
            for line in open(statusfile, 'r').readlines():
                if image in line:
                    last = line.rstrip()
                    break

        if last:
            # Linbo locale is en_GB, not necessarily the server locale
            saved = locale.setlocale(locale.LC_ALL)
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            last = datetime.strptime(last.split(' ')[0], '%Y%m%d%H%M')
            locale.setlocale(locale.LC_ALL, saved)
            last_tupln = time.mktime(last.timetuple())

        today = time.mktime(datetime.now().timetuple())

        date = datetime.strftime(
            last, '%d.%m.%Y %H:%M') if last_tupln else "Never"
        tmpDict = {
            'date': date
        }
        if date == "Never" or (today - last_tupln > 30*24*3600):
            tmpDict['status'] = "danger"
        elif today - last_tupln > 7*24*3600:
            tmpDict['status'] = "warning"
        else:
            tmpDict['status'] = "success"

        return tmpDict

    @post(r'/api/lmn/device-manager/getlinboremotelog')
    @authorize('lm:device-manager:read')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_getlinboremotelog(self, http_context):
        device = http_context.json_body()['device']
        path = os.path.join("/var/log/linuxmuster/linbo/",
                            device["hostname"] + ".linbo-remote")
        if os.path.isfile(path):
            command = ["tail", "-n", "30", path]
            r = subprocess.Popen(command, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, shell=False).stdout.read()
            return str(r.decode("utf-8"))
        return None

    @get(r'/api/lmn/device-manager/getrunninglinboremotecommands')
    @authorize('lm:device-manager:read')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_getrunninglinboremotecommands(self, http_context):
        result = []
        command = ["linbo-remote", "-l"]
        r = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, shell=False).stdout.readlines()
        for line in r:
            line = line.decode("utf-8").split()
            if "/tmp/tmux-0/default" not in line:
                result.append({"id": line[0], "pid": line[1], "filename": line[2],
                            "hostname": line[2].split(".")[0], "startdate": line[3].strip("()"),
                            "starttime": line[4].strip("()")})
        return result

    @get(r'/api/lmn/device-manager/getPrestartCommands')
    @authorize('lm:device-manager:read')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_getPrestartCommands(self, http_context):
        result = []
        dir_path = "/srv/linbo/linbocmd/"
        for path in os.listdir(dir_path):
            full_path = os.path.join(dir_path, path)
            if os.path.isfile(full_path):
                with open(full_path) as raw_file:
                    result.append(
                        {"name": path.split(".")[0], "path": full_path, "content": raw_file.read()})
        return result

    @post(r'/api/lmn/device-manager/removePrestartCommands')
    @authorize('lm:device-manager:modify')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_removePrestartCommands(self, http_context):
        preStartCommand = http_context.json_body()['preStartCommand']
        if os.path.isfile(preStartCommand["path"]):
            os.remove(preStartCommand["path"])
            return {"status": True, "message": ""}
        return {"status": False, "message": "File not found!"}

    @post(r'/api/lmn/device-manager/editPrestartCommands')
    @authorize('lm:device-manager:modify')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_editPrestartCommands(self, http_context):
        preStartCommand = http_context.json_body()['preStartCommand']
        newCommand = http_context.json_body()['newCommand']
        if os.path.isfile(preStartCommand["path"]):
            with open(preStartCommand["path"], "w") as raw_file:
                raw_file.write(newCommand)
                return {"status": True, "message": ""}
        return {"status": False, "message": "File not found!"}
