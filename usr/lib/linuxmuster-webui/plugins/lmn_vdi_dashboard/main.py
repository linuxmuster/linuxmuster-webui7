from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:class',
                'name': 'VDI Classroom',
                'icon': 'fas fa-laptop-house',
                'url': '/view/lmn_vdi_dashboard',
                'children': []
            }
        ]

# Uncomment the following lines to set a new permission
from aj.auth import PermissionProvider
@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lmn_vdi_dashboard:show',
                'name': _('VDI Dashboard permission'),
                'default': False,
            },
        ]