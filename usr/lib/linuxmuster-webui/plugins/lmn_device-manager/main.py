from jadi import component

from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                # category:tools, category:sofware, category:system, category:other
                'attach': 'category:devicemanagement',
                'name': 'Device-Manager',
                'icon': 'laptop',
                'url': '/view/lmn/device-manager',
                'weight': '10',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:device-manager:read',
                'name': _('View actual status and config of LINBO devices'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:device-manager:modify',
                'name': _('Manage LINBO devices'), # skipcq: PYL-E0602
                'default': False,
            },
        ]
