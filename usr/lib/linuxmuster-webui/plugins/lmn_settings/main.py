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
                'name': _('School Settings'), # skipcq: PYL-E0602
                'icon': 'sliders-h',
                'url': '/view/lmn/schoolsettings',
                'children': [],
                'weight': 40,
            },
            {
                'attach': 'category:schoolsettingsdefaults',
                'name': _('Global Settings'), # skipcq: PYL-E0602
                'icon': 'cogs',
                'url': '/view/lmn/globalsettings',
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
                'name': _('Configure school settings'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:globalsettings',
                'name': _('Configure global settings'), # skipcq: PYL-E0602
                'default': False,
            },
        ]
