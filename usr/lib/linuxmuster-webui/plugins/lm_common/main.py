from jadi import component
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': None,
                'id': 'category:usermanagement',
                'name': _('User Management'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:listmanagement',
                'name': _('List Management'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:quota',
                'name': _('Quota'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:devicemanagement',
                'name': _('Device Management'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:class',
                'name': _('Class'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:schoolsettingsdefaults',
                'name': _('School Settings'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:globalsettingsdefaults',
                'name': _('Global Settings'),
                'children': [
                ]
            },
        ]
