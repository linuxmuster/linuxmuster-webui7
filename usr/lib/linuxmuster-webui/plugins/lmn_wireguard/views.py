from jadi import component

from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

import requests
import json

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @post(r'/api/lmn/wireguard')
    @endpoint(api=True)
    def handle_api_lmn_wireguard(self, http_context):
        url = http_context.json_body()['url']
        method = http_context.json_body()['method']

        try:

            with open("/etc/linuxmuster/webui/wireguard/config.json") as f:
                config = json.load(f)

            if method == "GET":
                    req = requests.get(config["url"] + url, headers={ "LMN-API-Secret": config["secret"] }, verify=False)
                    if req.status_code == 200:
                        return req.json()

            elif method == "POST":
                data = http_context.json_body()['data']
                req = requests.post(config["url"] + url, json.dumps(data), headers={ "LMN-API-Secret": config["secret"] }, verify=False)
                if req.status_code == 200:
                    return req.json()

            elif method == "PUT":
                data = http_context.json_body()['data']
                req = requests.put(config["url"] + url, data, headers={ "LMN-API-Secret": config["secret"] }, verify=False)
                if req.status_code == 200:
                    return req.json()

            elif method == "DELETE":
                req = requests.delete(config["url"] + url, headers={ "LMN-API-Secret": config["secret"] }, verify=False)
                if req.status_code == 200:
                    return req.json()

            return False
        
        except:

            return False
