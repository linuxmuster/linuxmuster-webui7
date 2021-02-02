# coding=utf-8
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_getSophomorixValue
from aj.plugins.lmn_websession.api import loadList, bbbApiCall, getURL, replaceSpecialChars
from aj.plugins import PluginManager
from aj.plugins.lmn_common.api import LinuxmusterConfig, lmn_write_configfile

import aj
import json
import logging
import os
import random
import string
import urllib.parse

@component(HttpPlugin)
class Handler(HttpPlugin):

    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/websession/user-search')
    @endpoint(api=True)
    def handle_api_ldap_user_search(self, http_context):
        school = 'default-school'
        with authorize('lm:users:students:read'):
            try:
                sophomorixCommand = ['sophomorix-query', '-jj', '--schoolbase', school, '--user-basic', '--anyname', '*'+http_context.json_body()['q']+'*']
                users = lmn_getSophomorixValue(sophomorixCommand, 'USER', True)
            except Exception:
                return 0
        userList = []
        for user in users:
            userList.append(users[user])
        return userList

    @url(r'/api/lmn/websession/schoolClass-search')
    @endpoint(api=True)
    def handle_api_ldap_group_search(self, http_context):
        school = 'default-school'
        with authorize('lm:users:students:read'):
            try:
                sophomorixCommand = ['sophomorix-query', '-jj', '--schoolbase', school, '--class', '--group-members', '--user-full', '--sam', '*'+http_context.query['q']+'*']
                schoolClasses = lmn_getSophomorixValue(sophomorixCommand, 'MEMBERS', True)
            except Exception:
                return 0
        schoolClassList = []
        for schoolClass in schoolClasses:
            schoolClassJson = {}
            schoolClassJson['sophomorixAdminClass'] = schoolClass
            schoolClassJson['members'] = schoolClasses[schoolClass]
            schoolClassList.append(schoolClassJson)
        return schoolClassList

    @url(r'/api/lmn/websession/getWebConferenceEnabled')
    @endpoint(api=True)
    def handle_api_get_webConferenceEnabled(self, http_context):
        if http_context.method == 'GET':
            sessionList = loadList()
            if sessionList["status"] == "success":
                return True
            return False

    @url(r'/api/lmn/websession/getWebConferences')
    @endpoint(api=True)
    def handle_api_get_webConferences(self, http_context):
        if http_context.method == 'POST':
            username = http_context.json_body()['username']
            sessionList = loadList()
            webConferences = []
            if sessionList["status"] == "success":
                for session in sessionList["data"]:
                    if username in session["moderator"]:
                        webConferences.append(session)
                    for participant in session["participants"]:
                        if username == participant:
                            webConferences.append(session)
                for webConference in webConferences:
                    result = bbbApiCall("isMeetingRunning?meetingID=" + webConference["id"])
                    if result["running"] == "false":
                        webConferences[webConferences.index(webConference)]["status"] = "stopped"
                    else:
                        webConferences[webConferences.index(webConference)]["status"] = "started"
            return webConferences

    @url(r'/api/lmn/websession/getWebConferenceByName')
    @endpoint(api=True)
    def handle_api_get_webConferenceByName(self, http_context):
        if http_context.method == 'POST':
            sessionname = http_context.json_body()['sessionname']
            sessionList = loadList()
            if sessionList["status"] == "success":
                webConference = {"id": "0"}
                for session in sessionList["data"]:
                    if sessionname in session["sessionname"]:
                        webConference = session
                result = bbbApiCall("isMeetingRunning?meetingID=" + webConference["id"])
                if result["running"] == "false":
                    webConference["status"] = "stopped"
                else:
                    webConference["status"] = "started"
                if webConference == None:
                    return {"status": "ERROR"}
                else:
                    return {"status": "SUCCESS", "data": webConference}
            else:
                return {"status": "ERROR"}
    
    @url(r'/api/lmn/websession/createWebConference')
    @endpoint(api=True)
    def handle_api_create_webConference(self, http_context):
        if http_context.method == 'POST':
            data = http_context.json_body()
            path = "/etc/linuxmuster/webui/websession/websession_list.json"
            filedata = ""
            with open(path) as file:
                filedata = json.loads(file.read())
            data["status"] = "stopped"
            data["id"] = replaceSpecialChars(str(data["sessionname"] + "-" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))).replace(" ", ""))
            while data["id"] in filedata:
                data["id"] = replaceSpecialChars(str(data["sessionname"] + "-" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))).replace(" ", ""))
            data["attendeepw"] = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
            data["moderatorpw"] = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
            data["sessionname"] = replaceSpecialChars(data["sessionname"])
            filedata.append(data)
            with open(path, "w") as file:
                file.write(json.dumps(filedata, indent=4))
            return {"status": "SUCCESS", "id": data["id"], "attendeepw": data["attendeepw"], "moderatorpw": data["moderatorpw"]}

    @url(r'/api/lmn/websession/startWebConference')
    @endpoint(api=True)
    def handle_api_start_webConference(self, http_context):
        if http_context.method == 'POST':
            sessionname = urllib.parse.quote(http_context.json_body()["sessionname"])
            id = http_context.json_body()["id"]
            attendeepw = http_context.json_body()["attendeepw"]
            moderatorpw = http_context.json_body()["moderatorpw"]
            return bbbApiCall("create?attendeePW=" + attendeepw + "&meetingID=" + id + "&moderatorPW=" + moderatorpw + "&name=" + sessionname)

    @url(r'/api/lmn/websession/joinWebConference')
    @endpoint(api=True, auth=False)
    def handle_api_join_webConference(self, http_context):
        if http_context.method == 'POST':
            id = http_context.json_body()["id"]
            password = http_context.json_body()["password"]
            name = urllib.parse.quote(http_context.json_body()["name"])
            return getURL("join?fullName=" + name + "&meetingID=" + id + "&password=" + password + "&redirect=true")

    @url(r'/api/lmn/websession/endWebConference')
    @endpoint(api=True)
    def handle_api_stop_webConference(self, http_context):
        if http_context.method == 'POST':
            id = http_context.json_body()["id"]
            moderatorpw = http_context.json_body()["moderatorpw"]
            return bbbApiCall("end?meetingID=" + id + "&password=" + moderatorpw)

    @url(r'/api/lmn/websession/deleteWebConference')
    @endpoint(api=True)
    def handle_api_delete_webConference(self, http_context):
        if http_context.method == 'POST':
            id = http_context.json_body()["id"]
            path = "/etc/linuxmuster/webui/websession/websession_list.json"
            filedata = ""
            with open(path) as file:
                filedata = json.loads(file.read())
            for i in range(len(filedata)):
                if filedata[i]["id"] == id:
                    filedata.pop(i)
            with open(path, "w") as file:
                file.write(json.dumps(filedata, indent=4))
            return {"status": "SUCCESS"}


    @url(r'/api/lmn/websession/hasPassword')
    @endpoint(api=True, auth=False)
    def handle_api_hasPassword_webConference(self, http_context):
        if http_context.method == 'POST':
            id = http_context.json_body()["id"]
            sessionList = loadList()
            for session in sessionList:
                if session["id"] == id:
                    return session["sessiontype"]

    @url(r'/api/lmn/websession/getSessionName')
    @endpoint(api=True, auth=False)
    def handle_api_getSessionName_webConference(self, http_context):
        if http_context.method == 'POST':
            id = http_context.json_body()["id"]
            sessionList = loadList()
            for session in sessionList:
                if session["id"] == id:
                    return session["sessionname"]

    @url(r'/api/lmn/websession/checkPassword')
    @endpoint(api=True, auth=False)
    def handle_api_checkPassword_webConference(self, http_context):
        if http_context.method == 'POST':
            id = http_context.json_body()["id"]
            password = http_context.json_body()["password"]
            sessionList = loadList()
            for session in sessionList:
                if session["id"] == id:
                    if session["sessionpassword"] == password:
                        return session["attendeepw"]
            return "error"

    @url(r'/api/lmn/websession/isRunning')
    @endpoint(api=True, auth=False)
    def handle_api_isRunning_webConference(self, http_context):
        if http_context.method == 'POST':
            id = http_context.json_body()["id"]
            result = bbbApiCall("isMeetingRunning?meetingID=" + id)
            if result["running"] == "false":
                return False
            else:
                return True

    @url('/websession/(?P<name>.+)')
    @endpoint(page=True, auth=False)
    def handle_view(self, http_context, name):
        manager = PluginManager.get(aj.context)
        path = manager.get_content_path('lmn_websession', 'resources/partial/public.html')
        content = open(path).read() 
        http_context.add_header('Content-Type', 'text/html')
        http_context.respond_ok()
        return content