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
                'name': _('Devices'), # skipcq: PYL-E0602
                'icon': 'laptop',
                'url': '/view/lmn/devices',
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
                'name': _('Read/write devices'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:devices:import',
                'name': _('Import device'), # skipcq: PYL-E0602
                'default': False,
            },
        ]
