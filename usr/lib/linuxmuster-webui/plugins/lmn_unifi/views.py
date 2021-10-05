from jadi import component

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

import logging

from aj.plugins.lmn_unifi.niunificontrol import getConfig, initAPI, getDevicesList, enableDevice, disableDevice, getSshConfig, rebootDevice

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/unifi/getDevices')
    @endpoint(api=True)
    def handle_api_example_ni_unifi(self, http_context):
        if http_context.method == 'GET':
            config = getConfig("/etc/linuxmuster/webui/unifi/unifi-control.conf")
            unifiApi = initAPI(config["username"], config["password"], config["baseurl"])
            deviceList = getDevicesList(config, unifiApi)
            deviceArray = []
            for device in deviceList:
                if deviceList[device]["DEVICE_NAME"] != "" and deviceList[device]["DEVICE_TYPE"] == "uap":
                    deviceList[device]["selected"] = False
                    deviceArray.append(deviceList[device])
            return {"status": "success", "data": deviceArray}

    @url(r'/api/lmn/unifi/rebootDevice')
    @endpoint(api=True)
    def handle_api_example_ni_unifi_reboot(self, http_context):
        if http_context.method == 'POST':
            device = http_context.json_body()['device']
            config = getConfig("/etc/linuxmuster/webui/unifi/unifi-control.conf")
            unifiApi = initAPI(config["username"], config["password"], config["baseurl"])
            sshconfig = getSshConfig(config, unifiApi, device["SITE"])
            return rebootDevice(device["DEVICE_IP"], sshconfig)

    @url(r'/api/lmn/unifi/enableDevice')
    @endpoint(api=True)
    def handle_api_example_ni_unifi_enable(self, http_context):
        if http_context.method == 'POST':
            device = http_context.json_body()['device']
            config = getConfig("/etc/linuxmuster/webui/unifi/unifi-control.conf")
            unifiApi = initAPI(config["username"], config["password"], config["baseurl"])
            return enableDevice(device, unifiApi)

    @url(r'/api/lmn/unifi/disableDevice')
    @endpoint(api=True)
    def handle_api_example_ni_unifi_disable(self, http_context):
        if http_context.method == 'POST':
            device = http_context.json_body()['device']
            config = getConfig("/etc/linuxmuster/webui/unifi/unifi-control.conf")
            unifiApi = initAPI(config["username"], config["password"], config["baseurl"])
            return disableDevice(device, unifiApi)

    
