from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:general',
                'name': 'My files',
                'icon': 'fas fa-folder-open',
                'url': '/view/lmn/home',
                'children': []
            }
        ]

