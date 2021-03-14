from jadi import component

from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider
import aj

if aj.dev:
    @component(SidebarItemProvider)
    class ItemProvider(SidebarItemProvider):
        def __init__(self, context):
            self.context = context

        def provide(self):
            return [
                {
                    'attach': 'category:tools',
                    'id': 'permissions',
                    'name': _('Permissions'),
                    'icon': 'fas fa-user-lock',
                    'url': '/view/permissions',
                    'children': [],
                }
            ]
