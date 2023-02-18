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
                'attach': 'category:system',
                'name': 'Cron',
                'icon': 'clock-o',
                'url': '/view/lmn/crontab',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:crontab:read',
                'name': _('Get the crontab command of the user'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:crontab:write',
                'name': _('Modify the crontab of the user'), # skipcq: PYL-E0602
                'default': False,
            },
        ]
