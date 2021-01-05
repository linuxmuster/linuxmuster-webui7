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
            'attach': 'category:class',
            'name': _('Session'), # skipcq: PYL-E0602
            'icon': 'chalkboard-teacher',
            'url': '/view/lmn/session',
            'weight': 20,
            },
            {
            'attach': 'category:class',
            'name': _('Print Passwords'), # skipcq: PYL-E0602
            'icon': 'key',
            'url': '/view/lm/users/print-passwords',
            'weight': 40,
            }
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:users:teachers:write',
                'name': _('Write students'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lmn:session:trans',
                'name': _('Transfer Files in Session'), # skipcq: PYL-E0602
                'default': False,
            },
        ]
