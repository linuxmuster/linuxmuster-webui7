from jadi import component
from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    '''
    To add a sidebar item, we create a component implementing SidebarItemProvider
    '''
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                # attach the item to the 'general' category
                'attach': 'category:classroom',
                'name': 'Session',
                'icon': 'users',
                'url': '/view/lmn/session',
                'children': []
            }
        ]
