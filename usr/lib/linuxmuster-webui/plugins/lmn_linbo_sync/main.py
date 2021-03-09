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
                'id': 'sync',
                'name': _('Linbo synchronization'),
                'icon': 'fas fa-sync-alt',
                'url': '/view/lmn/linbo_sync',
                'children': [],
            }
        ]


@component(PermissionProvider)
class Permissions(PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:sync:list',
                'name': _('List of last sync workstations'),
                'default': False,
            },
            {
                'id': 'lm:sync:online',
                'name': _('Test if workstation is up'),
                'default': False,
            },
            {
                'id': 'lm:sync:sync',
                'name': _('Synchronize first OS from workstation'),
                'default': False,
            },
        ]
