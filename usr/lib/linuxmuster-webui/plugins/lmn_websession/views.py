# coding=utf-8
from jadi import component
from aj.api.http import post, get, delete, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.lmn_websession.api import loadList, bbbApiCall, getURL, replaceSpecialChars
from aj.plugins import PluginManager

import aj
import json
import random
import string
import urllib.parse

@component(HttpPlugin)
class Handler(HttpPlugin):

    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/websession/webConferenceEnabled')
    @endpoint(api=True)
    def handle_api_get_webConferenceEnabled(self, http_context):
        sessionList = loadList()
        if sessionList["status"] == "success":
            return True
        return False

    @get(r'/api/lmn/websession/webConferences')
    @endpoint(api=True)
    def handle_api_get_webConferences(self, http_context):
        username = self.context.identity
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

    @get(r'/api/lmn/websession/webConferences/(?P<sessionname>.*)')
    @endpoint(api=True)
    def handle_api_get_webConferenceByName(self, http_context, sessionname=''):
        sessionList = loadList()
        if sessionList["status"] == "success":
            webConference = {"id": "0"}
            for session in sessionList["data"]:
                # TODO : maybe prefix problem in sessionname
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
    
    @post(r'/api/lmn/websession/webConferences')
    @endpoint(api=True)
    def handle_api_create_webConference(self, http_context):
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
        data["moderator"] = self.context.identity
        filedata.append(data)
        with open(path, "w") as file:
            file.write(json.dumps(filedata, indent=4))
        return {"status": "SUCCESS", "id": data["id"], "attendeepw": data["attendeepw"], "moderatorpw": data["moderatorpw"]}

    @post(r'/api/lmn/websession/startWebConference')
    @endpoint(api=True)
    def handle_api_start_webConference(self, http_context):
        sessionname = urllib.parse.quote(http_context.json_body()["sessionname"])
        id = http_context.json_body()["id"]
        attendeepw = http_context.json_body()["attendeepw"]
        moderatorpw = http_context.json_body()["moderatorpw"]
        return bbbApiCall("create?attendeePW=" + attendeepw + "&meetingID=" + id + "&moderatorPW=" + moderatorpw + "&name=" + sessionname)

    @post(r'/api/lmn/websession/joinWebConference')
    @endpoint(api=True, auth=False)
    def handle_api_join_webConference(self, http_context):
        id = http_context.json_body()["id"]
        password = http_context.json_body()["password"]
        name = urllib.parse.quote(http_context.json_body()["name"])
        return getURL("join?fullName=" + name + "&meetingID=" + id + "&password=" + password + "&redirect=true")

    @post(r'/api/lmn/websession/endWebConference')
    @endpoint(api=True)
    def handle_api_stop_webConference(self, http_context):
        id = http_context.json_body()["id"]
        moderatorpw = http_context.json_body()["moderatorpw"]
        return bbbApiCall("end?meetingID=" + id + "&password=" + moderatorpw)

    @delete(r'/api/lmn/websession/webConference/(?P<id>.*)')
    @endpoint(api=True)
    def handle_api_delete_webConference(self, http_context, id):
        path = "/etc/linuxmuster/webui/websession/websession_list.json"
        filedata = ""
        with open(path) as file:
            filedata = json.loads(file.read())
        for i in range(len(filedata)):
            if filedata[i]["id"] == id:
                filedata.pop(i)
                break
        with open(path, "w") as file:
            file.write(json.dumps(filedata, indent=4))
        return {"status": "SUCCESS"}

    # TODO : should be GET request
    @post(r'/api/lmn/websession/session/hasPassword')
    @endpoint(api=True, auth=False)
    def handle_api_hasPassword_webConference(self, http_context):
        id = http_context.json_body()["id"]
        sessionList = loadList()
        if sessionList["status"] == "success":
            for session in sessionList["data"]:
                if session["id"] == id:
                    return session["sessiontype"]
        else:
            return "error"

    # TODO : should be GET request
    @post(r'/api/lmn/websession/session/name')
    @endpoint(api=True, auth=False)
    def handle_api_getSessionName_webConference(self, http_context):
        id = http_context.json_body()["id"]
        sessionList = loadList()
        if sessionList["status"] == "success":
            for session in sessionList["data"]:
                print(session)
                if str(session["id"]) == str(id):
                    return session["sessionname"]
        else:
            return "error"

    @post(r'/api/lmn/websession/session/checkPassword')
    @endpoint(api=True, auth=False)
    def handle_api_checkPassword_webConference(self, http_context):
        id = http_context.json_body()["id"]
        password = http_context.json_body()["password"]
        sessionList = loadList()
        if sessionList["status"] == "success":
            for session in sessionList["data"]:
                if session["id"] == id:
                    if session["sessionpassword"] == password:
                        return session["attendeepw"]
            return "error"
        else:
            return "error"

    # TODO : should be GET request
    @post(r'/api/lmn/websession/session/isRunning')
    @endpoint(api=True, auth=False)
    def handle_api_isRunning_webConference(self, http_context):
        id = http_context.json_body()["id"]
        result = bbbApiCall("isMeetingRunning?meetingID=" + id)
        if result["running"] == "false":
            return False
        else:
            return True

    @get('/websession/(?P<name>.+)')
    @endpoint(page=True, auth=False)
    def handle_view(self, http_context, name):
        manager = PluginManager.get(aj.context)
        path = manager.get_content_path('lmn_websession', 'resources/partial/public.html')
        content = open(path).read() 
        http_context.add_header('Content-Type', 'text/html')
        http_context.respond_ok()
        return content