from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider
from aj.auth import PermissionProvider

@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:software',
                'name': 'Docker',
                'icon': 'fab fa-docker',
                'url': '/view/lmn/docker',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:docker:list',
                'name': _('List image and running containers'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:docker:change',
                'name': _('Remove images and change running containers'), # skipcq: PYL-E0602
                'default': False,
            },
        ]
