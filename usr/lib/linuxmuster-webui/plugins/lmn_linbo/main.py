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
                'attach': 'category:devicemanagement',
                'name': _('LINBO'),  # skipcq: PYL-E0602
                'icon': 'laptop-medical',
                'url': '/view/lm/linbo',
                'weight': 15,
                'children': [],
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:linbo:configs',
                'name': _('Read/write start.conf'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:linbo:images',
                'name': _('Read/write images'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:linbo:examples',
                'name': _('Read examples'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:linbo:icons',
                'name': _('Read/write icons'), # skipcq: PYL-E0602
                'default': False,
            },
        ]
