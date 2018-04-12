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
                'name': _('Students'),
                'icon': 'users',
                'url': '/view/lm/users/students',
                'weight': 10,
            },
            {
                'attach': 'category:usermanagement',
                'name': _('Teachers'),
                'icon': 'briefcase',
                'url': '/view/lm/users/teachers',
                'weight': 15,
                'children': [
                    {
                        'name': _('Teachers List'),
                        'icon': 'briefcase',
                        'url': '/view/lm/users/teachers',
                        'weight': 10,
                    },
                    {
                        'name': _('Teacher Passwords'),
                        'icon': 'key',
                        'url': '/view/lm/users/teacher-passwords',
                        'weight': 15,
                    },
                    {
                        'name': _('ATi Teacher Passwords'),
                        'icon': 'key',
                        'url': '/view/lm/users/ati-teacher-passwords',
                        'weight': 15,
                    },
                ],
            },
            {
                'attach': 'category:usermanagement',
                'name': _('Extra Users'),
                'icon': 'users',
                'url': '/view/lm/users/extra-students',
                'weight': 20,
                'children': [
                    {
                        'name': _('Extra Students'),
                        'icon': 'users',
                        'url': '/view/lm/users/extra-students',
                        'weight': 25,
                    },
                    {
                        'name': _('Extra Courses'),
                        'icon': 'users',
                        'url': '/view/lm/users/extra-courses',
                        'weight': 30,
                    },
                ],
            },
            {
                'attach': 'category:usermanagement',
                'name': _('Print Passwords'),
                'icon': 'print',
                'url': '/view/lm/users/print-passwords',
                'weight': 25,
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:users:students:read',
                'name': _('Read students'),
                'default': False,
            },
            {
                'id': 'lm:users:students:write',
                'name': _('Write students'),
                'default': False,
            },
            {
                'id': 'lm:users:teachers:read',
                'name': _('Read teachers'),
                'default': False,
            },
            {
                'id': 'lm:users:teachers:write',
                'name': _('Write teachers'),
                'default': False,
            },
            {
                'id': 'lm:users:extra-students:read',
                'name': _('Read extra students'),
                'default': False,
            },
            {
                'id': 'lm:users:extra-students:write',
                'name': _('Write extra students'),
                'default': False,
            },
            {
                'id': 'lm:users:extra-courses:read',
                'name': _('Read extra courses'),
                'default': False,
            },
            {
                'id': 'lm:users:extra-courses:write',
                'name': _('Write extra courses'),
                'default': False,
            },
            {
                'id': 'lm:users:check',
                'name': _('Check user changes'),
                'default': False,
            },
            {
                'id': 'lm:users:apply',
                'name': _('Apply user changes'),
                'default': False,
            },
            {
                'id': 'lm:users:passwords',
                'name': _('Read/write passwords'),
                'default': False,
            },
        ]
