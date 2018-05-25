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
                'attach': 'category:schoolsettingsdefaults',
                'name': _('Settings'),
                'icon': 'wrench',
                'url': '/view/lm/schoolsettings',
                'children': [],
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:settings',
                'name': _('Configure settings'),
                'default': False,
            },
        ]
