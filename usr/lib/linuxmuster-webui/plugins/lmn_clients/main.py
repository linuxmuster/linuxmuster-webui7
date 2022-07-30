from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider
from aj.auth import PermissionProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:devicemanagement',
                'name': _('Client configuration'), # skipcq: PYL-E0602
                'icon': 'fas fa-toolbox',
                'url': '/view/lmn_clients',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lmn:clients:config',
                'name': _('Configure clients features'),
                'default': False,
            },
        ]