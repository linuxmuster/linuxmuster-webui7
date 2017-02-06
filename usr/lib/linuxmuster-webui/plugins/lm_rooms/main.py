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
                'attach': 'category:settingsdefaults',
                'name': _('Rooms'),
                'icon': 'tasks',
                'url': '/view/lm/room-defaults',
                'children': [],
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:rooms:configure',
                'name': _('Configure room defaults'),
                'default': True,
            },
            {
                'id': 'lm:rooms:apply',
                'name': _('Set room defaults'),
                'default': True,
            },
        ]
