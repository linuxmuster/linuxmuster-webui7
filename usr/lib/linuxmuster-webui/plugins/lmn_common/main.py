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
                'name': _('User Management'), # skipcq: PYL-E0602
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:listmanagement',
                'name': _('List Management'), # skipcq: PYL-E0602
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:quota',
                'name': _('Quota'), # skipcq: PYL-E0602
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:devicemanagement',
                'name': _('Device Management'), # skipcq: PYL-E0602
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:class',
                'name': _('Classroom'), # skipcq: PYL-E0602
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:schoolsettingsdefaults',
                'name': _('Settings'), # skipcq: PYL-E0602
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:globalsettingsdefaults',
                'name': _('Global Settings'), # skipcq: PYL-E0602
                'children': [
                ]
            },
        ]
