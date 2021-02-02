from jadi import component

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    # Register URL for this api
    @url(r'/api/lmn_vdi_dashboard')
    # Set the right permissions if necessary, see main.py to activate it.
    #@authorize('lmn_vdi_dashboard:show')
    @endpoint(api=True)
    def handle_api_example_lmn_vdi_dashboard(self, http_context):
        if http_context.method == 'POST':
            action = http_context.json_body()['action']
            if action == 'get-vdiSession':
                username = http_context.json_body()['username']
                group = http_context.json_body()['group']
                createSessionCommand = ['/usr/lib/linuxmuster-linbo-vdi/getConnection.py', group, username]
                output = subprocess.check_output(createSessionCommand, shell=False)
                output = json.loads(output.decode())
                path = os.path.abspath(os.path.join('/tmp/vdi/', name))
                if not path.startswith(root):
                    return http_context.respond_forbidden()
                return http_context.file(path, inline=False, name=name.encode())
        
