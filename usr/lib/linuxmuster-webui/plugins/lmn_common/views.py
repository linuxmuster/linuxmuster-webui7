import os

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/log(?P<path>.+)')
    @endpoint(api=True)
    def handle_api_log(self, http_context, path=None):
        if not os.path.exists(path):
            return ''
        with open(path) as f:
            f.seek(int(http_context.query.get('offset', '0')))
            return f.read()
            
    @url(r'/api/lm/remove-file') ## TODO authorize
    @endpoint(api=True)
    def handle_api_remove_file(self, http_context):
        if http_context.method == 'POST':
            filepath = '/etc/linuxmuster/sophomorix/default-school/' + http_context.json_body()['filepath']
            if not os.path.exists(filepath):
                return
            else:
                os.unlink(filepath)
                return True
