from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                # category:tools, category:sofware, category:system, category:other
                'attach': 'category:general',
                'name': 'Lmn_landing',
                # http://fontawesome.io/icons/
                'icon': 'question',
                'url': '/view/lmn_landing',
                'children': []
            }
        ]
