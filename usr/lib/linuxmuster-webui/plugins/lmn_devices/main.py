from jadi import component
from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:devicemanagement',
                'name': _('Devices'),
                'icon': 'laptop',
                'url': '/view/lm/devices',
                'weight': 10,
                'children': [],
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:devices',
                'name': _('Read/write devices'),
                'default': False,
            },
            {
                'id': 'lm:devices:import',
                'name': _('Import device'),
                'default': False,
            },
            {
                'id': 'lm:leases',
                'name': _('Request DHCP leases'),
                'default': False,
            },
        ]
