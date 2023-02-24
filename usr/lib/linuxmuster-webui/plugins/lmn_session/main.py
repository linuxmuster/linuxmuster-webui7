from jadi import component
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
            'attach': 'category:class',
            'name': _('Session'),
            'icon': 'chalkboard-teacher',
            'url': '/view/lmn/oldsession',
            'weight': 15,
            },
        ]

