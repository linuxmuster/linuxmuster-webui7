from jadi import component

from aj.api.http import get, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

from aj.plugins.lmn_nextcloud.api import loadSettings

import urllib3

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/nextcloud')
    @endpoint(api=True)
    def handle_api_example_ni_nextcloud(self, http_context):
        settings = loadSettings()
        if settings["status"] == "success":
            link = settings["data"]['settings']['nextcloudURL']
            fullscreen = settings["data"]['settings']['toggleFullscreen']
            askuser = settings["data"]['settings']['askForUser']
            try:
                resp = urllib3.PoolManager(cert_reqs='CERT_NONE').request('GET', link)
                code = int(resp.status)
                if code == 200:
                    return [code, link, fullscreen, askuser]
                return [code, None, None, None]
            except:
                return [0, None, None, None]
        else:
            return [0, None, None, None]
