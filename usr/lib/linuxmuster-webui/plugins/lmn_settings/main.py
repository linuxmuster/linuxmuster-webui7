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
                'name': _('School Settings'),
                'icon': 'wrench',
                'url': '/view/lm/schoolsettings',
                'children': [],
                'weight': 40,
            },
            {
                'attach': 'category:schoolsettingsdefaults',
                'name': _('Global Settings'),
                'icon': 'cog',
                'url': '/view/lm/globalsettings',
                'children': [],
                'weight': 55,
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:schoolsettings',
                'name': _('Configure school settings'),
                'default': False,
            },
            {
                'id': 'lm:globalsettings',
                'name': _('Configure global settings'),
                'default': False,
            },
        ]
