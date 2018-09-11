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
                'attach': 'category:usermanagement',
                'name': _('Groupmembership'),
                'icon': 'wrench',
                'url': '/view/lmn/groupmembership',
                'children': [],
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lmn:groupmembership',
                'name': _('Edit Groupmemberships'),
                'default': False,
            },
        ]
