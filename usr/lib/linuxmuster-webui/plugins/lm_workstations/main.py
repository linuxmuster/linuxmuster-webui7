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
                'name': _('Workstations'),
                'icon': 'laptop',
                'url': '/view/lm/workstations',
                'weight': 10,
                'children': [],
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:workstations',
                'name': _('Read/write workstations'),
                'default': False,
            },
            {
                'id': 'lm:workstations:import',
                'name': _('Import workstation'),
                'default': False,
            },
        ]
