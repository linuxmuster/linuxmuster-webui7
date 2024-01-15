from jadi import component
from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:usermanagement',
                'name': _('Teachers'), # skipcq: PYL-E0602
                'icon': 'user-tie',
                'url': '/view/lmn/users/teachers',
                'weight': 15,
            },
            {
                'attach': 'category:usermanagement',
                'name': _('Students'), # skipcq: PYL-E0602
                'icon': 'user-graduate',
                'url': '/view/lmn/users/students',
                'weight': 15,
            },
            {
                'attach': 'category:usermanagement',
                'name': _('School-Admins'), # skipcq: PYL-E0602
                'icon': 'user-ninja',
                'url': '/view/lmn/users/schooladmins',
                'weight': 20,
            },
            {
                'attach': 'category:usermanagement',
                'name': _('Global-Admins'), # skipcq: PYL-E0602
                'icon': 'user-astronaut',
                'url': '/view/lmn/users/globaladmins',
                'weight': 21,
            },
            {
                'attach': 'category:usermanagement',
                'name': _('Listmanagement'), # skipcq: PYL-E0602
                'icon': 'list',
                'url': '/view/lmn/users/listmanagement',
                'weight': 21,
            },
            {
                'attach': 'category:class',
                'name': _('Print Passwords'),
                'icon': 'key',
                'url': '/view/lmn/users/print-passwords',
                'weight': 40,
            }
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:users:students:read',
                'name': _('Read students'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:students:write',
                'name': _('Write students'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:teachers:read',
                'name': _('Read teachers'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:teachers:list',
                'name': _('List teachers'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:teachers:write',
                'name': _('Write teachers'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:schooladmins:read',
                'name': _('Read schooladmins'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:schooladmins:write',
                'name': _('Write schooladmins'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:globaladmins:read',
                'name': _('Read globaladmins'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:globaladmins:write',
                'name': _('Write globaladmins'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:extrastudents:read',
                'name': _('Read extra students'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:extrastudents:write',
                'name': _('Write extra students'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:extraclasses:read',
                'name': _('Read extra courses'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:extraclasses:write',
                'name': _('Write extra courses'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:check',
                'name': _('Check user changes'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:apply',
                'name': _('Apply user changes'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:passwords',
                'name': _('Read/write passwords'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:schooladmins:create',
                'name': _('Add school admins'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:globaladmins:create',
                'name': _('Add global admins'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:schooladmins:delete',
                'name': _('Delete school admins'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:globaladmins:delete',
                'name': _('Delete global admins'), # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:customfields:write',
                'name': _('Change own custom fields values'),  # skipcq: PYL-E0602
                'default': False,
            },
            {
                'id': 'lm:users:customfields:read',
                'name': _('Read custom fields values'),  # skipcq: PYL-E0602
                'default': False,
            },
        ]
