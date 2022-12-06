from jadi import component

from aj.api.http import get, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

from aj.plugins.lmn_links.api import loadList

import logging

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/links')
    @endpoint(api=True)
    def handle_api_example_ni_links(self, http_context):
        linkList = loadList()
        return linkList
