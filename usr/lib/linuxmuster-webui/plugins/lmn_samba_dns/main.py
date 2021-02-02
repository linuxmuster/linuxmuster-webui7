from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:system',
                'name': 'Samba DNS',
                'icon': 'exchange-alt',
                'url': '/view/samba_dns',
                'children': []
            }
        ]

# Uncomment the following lines to set a new permission
# from aj.auth import PermissionProvider
# @component(PermissionProvider)
# class Permissions (PermissionProvider):
#     def provide(self):
#         return [
#             {
#                 'id': 'extra_samba_dns:show',
#                 'name': _('Show the Python binding example'),
#                 'default': False,
#             },
#         ]