from jadi import component
from aj.plugins.core.api.sidebar import SidebarItemProvider
from aj.auth import PermissionProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:devicemanagement',
                'name': _('Printers'),
                'icon': 'print',
                'url': '/view/lm/printers',
                'weight': 20,
                'children': [],
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:printers',
                'name': _('Configure printers'),
                'default': True,
            },
        ]
