from jadi import component

from aj.auth import authorize
from aj.api.http import post, get, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from linuxmusterTools.lmnfile import LMNFile
from linuxmusterTools.linbo import last_sync, list_onboot_commands

import os
import nmap
import subprocess
import time
import logging

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
            command = ["ssh", device["hostname"], "-l", "root", "init 0"]

        elif device["os"] == "Windows":
            try:
                with open("/etc/linuxmuster/.secret/administrator", "r") as f:
                    password = f.read().strip()
            except FileNotFoundError:
                return {"status": False, "exitcode": None, "message": "Administrator password file not found!"}
            command = ["net", "rpc", "-S", device["hostname"], "-U",
                       f"administrator%{password}", "shutdown", "-t", "1", "-f"]

        else:
            return {"status": False, "exitcode": None, "message": "Could not determine os!"}

        r = subprocess.Popen(command, sensitive=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = r.stdout.read().decode("utf-8")
        logging.debug("Shutdown-Command-Result: %s" % result)
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
            command = ["ssh", device["hostname"], "-l", "root", "init 6"]

        elif device["os"] == "Windows":
            try:
                with open("/etc/linuxmuster/.secret/administrator", "r") as f:
                    password = f.read().strip()
            except FileNotFoundError:
                return {"status": False, "exitcode": None, "message": "Administrator password file not found!"}
            command = ["net", "rpc", "-S", device["hostname"], "-U",
                       f"administrator%{password}", "shutdown", "-r", "-t", "1", "-f"]

        else:
            return {"status": False, "exitcode": None, "message": "Could not determine os!"}

        r = subprocess.Popen(command, sensitive=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = r.stdout.read().decode("utf-8")
        logging.debug("Reboot-Command-Result: %s" % result)
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

    # /api/lmn/device-manager/run was removed: it ran any command sent by the
    # client as root. This plugin is obsolete, its "run" button no longer works.

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
        # Parsing of the *_image.status files belongs to linuxmusterTools:
        # last_sync() matches the image name exactly (and its .qdiff
        # variant), keeps the most recent entry and returns an epoch in
        # server local time, or False if the host never synced that image.
        last_tupln = last_sync(device["hostname"], image)
        today = time.time()

        date = datetime.fromtimestamp(last_tupln).strftime(
            '%d.%m.%Y %H:%M') if last_tupln else "Never"
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
        # Restrict to selected school
        hosts = {cn.lower() for cn in self.context.ldapreader.getval('/devices', 'cn', school=self.context.schoolmgr.school)}

        # list_onboot_commands() never returns the "linbo:<password>" entry,
        # which is the LINBO rsync password in clear.
        return [
            {
                "name": onboot["hostname"],
                "path": f"/srv/linbo/linbocmd/{onboot['hostname']}.cmd",
                "content": ",".join(onboot["commands"]),
            }
            for onboot in list_onboot_commands()
            if onboot["hostname"].lower() in hosts
        ]

    @post(r'/api/lmn/device-manager/removePrestartCommands')
    @authorize('lm:device-manager:modify')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_removePrestartCommands(self, http_context):
        preStartCommand = http_context.json_body()['preStartCommand']
        path = os.path.realpath(preStartCommand["path"])

        # Restrict to selected school
        hosts = {cn.lower() for cn in self.context.ldapreader.getval('/devices', 'cn', school=self.context.schoolmgr.school)}

        if (os.path.dirname(path) != os.path.realpath("/srv/linbo/linbocmd")
                or os.path.splitext(os.path.basename(path))[0].lower() not in hosts):
            return http_context.respond_forbidden()
        if os.path.isfile(path):
            os.remove(path)
            return {"status": True, "message": ""}
        return {"status": False, "message": "File not found!"}

    @post(r'/api/lmn/device-manager/editPrestartCommands')
    @authorize('lm:device-manager:modify')
    @endpoint(api=True)
    def handle_api_lmn_devicemanager_editPrestartCommands(self, http_context):
        preStartCommand = http_context.json_body()['preStartCommand']
        newCommand = http_context.json_body()['newCommand']
        path = os.path.realpath(preStartCommand["path"])

        # Restrict to selected school
        hosts = {cn.lower() for cn in self.context.ldapreader.getval('/devices', 'cn', school=self.context.schoolmgr.school)}

        if (os.path.dirname(path) != os.path.realpath("/srv/linbo/linbocmd")
                or os.path.splitext(os.path.basename(path))[0].lower() not in hosts):
            return http_context.respond_forbidden()
        if os.path.isfile(path):
            # Keep the rsync credentials hidden by getPrestartCommands, needed
            # by a pending upload, after a leading "dryrun" like linbo-remote -p.
            with open(path) as raw_file:
                secrets = [cmd for cmd in raw_file.read().strip().split(',') if cmd.startswith('linbo:')]
            commands = [cmd for cmd in newCommand.strip().split(',') if cmd and not cmd.startswith('linbo:')]
            start = 1 if commands[:1] == ['dryrun'] else 0
            commands[start:start] = secrets
            with open(path, "w") as raw_file:
                raw_file.write(','.join(commands) + '\n')
                return {"status": True, "message": ""}
        return {"status": False, "message": "File not found!"}
