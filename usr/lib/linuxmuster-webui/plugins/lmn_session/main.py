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
            'attach': 'category:class',
            'name': _('Session deprecated'),
            'icon': 'chalkboard-teacher',
            'url': '/view/lmn/oldsession',
            'weight': 15,
            },
            # {
            # 'attach': 'category:class',
            # 'name': _('Print Passwords'),
            # 'icon': 'key',
            # 'url': '/view/lmn/users/print-passwords',
            # 'weight': 40,
            # }
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:users:teachers:write',
                'name': _('Write students'),
                'default': False,
            },
            {
                'id': 'lmn:oldsession:trans',
                'name': _('Transfer Files in Session'),
                'default': False,
            },
        ]