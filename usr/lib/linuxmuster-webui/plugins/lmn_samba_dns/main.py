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
                'attach': 'category:system',
                'name': 'Samba DNS',
                'icon': 'exchange-alt',
                'url': '/view/lmn/samba_dns',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:samba_dns:read',
                'name': _('Show the DNS in Samba'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:samba_dns:write',
                'name': _('Change the DNS in Samba'), # skipcq: PYL-E0602
                'default': False,
            },
        ]
