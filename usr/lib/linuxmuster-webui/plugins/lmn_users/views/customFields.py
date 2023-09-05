"""
API for custom fields management.
"""

import os

from jadi import component
from aj.api.http import get, post, patch, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @post(r'/api/lmn/users/(?P<user>[a-z0-9\-_]*)/custom/(?P<index>[1-5])')
    @authorize('lm:users:customfields:write')
    @endpoint(api=True)
    def handle_update_custom(self, http_context, user, index):
        """
        Update a custom sophomorix field.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if os.getuid() != 0 and user != self.context.identity:
            return

        value = http_context.json_body()['value']

        try:
            command = ['sophomorix-user', '-u', user, f'--custom{index}', value, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

    @post(r'/api/lmn/users/(?P<user>[a-z0-9\-_]*)/custommulti/(?P<index>[1-5])')
    @authorize('lm:users:customfields:write')
    @endpoint(api=True)
    def handle_custom_mutli_add(self, http_context, user, index):
        """
        Add a sophomorix field in custom multi.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if os.getuid() != 0 and user != self.context.identity:
            return

        value = http_context.json_body()['value']

        try:
            command = ['sophomorix-user', '-u', user, f'--add-custom-multi{index}', value, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

    @patch(r'/api/lmn/users/(?P<user>[a-z0-9\-_]*)/custommulti/(?P<index>[1-5])')
    @authorize('lm:users:customfields:write')
    @endpoint(api=True)
    def handle_custom_multi_remove(self, http_context, user, index):
        """
        Remove a sophomorix field in custom multi.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if os.getuid() != 0 and user != self.context.identity:
            return

        value = http_context.json_body()['value']

        try:
            command = ['sophomorix-user', '-u', user, f'--remove-custom-multi{index}', value, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

    @post(r'/api/lmn/users/(?P<user>[a-z0-9\-_]*)/proxyaddresses')
    @authorize('lm:users:customfields:write')
    @endpoint(api=True)
    def handle_add_proxy_addresses(self, http_context, user):
        """
        Add an email in proxyAddresses, e.g. emails, for an user.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if os.getuid() != 0 and user != self.context.identity:
            return

        address = http_context.json_body()['address']

        try:
            command = ['sophomorix-user', '-u', user, f'--add-proxy-addresses', address, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

    @patch(r'/api/lmn/users/(?P<user>[a-z0-9\-_]*)/proxyaddresses')
    @authorize('lm:users:customfields:write')
    @endpoint(api=True)
    def handle_remove_proxy_addresses(self, http_context, user):
        """
        Remove an email in proxyAddresses, e.g. emails, for an user.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if os.getuid() != 0 and user != self.context.identity:
            return

        address = http_context.json_body()['address']

        try:
            command = ['sophomorix-user', '-u', user, f'--remove-proxy-addresses',
                       address, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

    @get(r'/api/lmn/users/(?P<user>[a-z0-9\-_]*)/customfields')
    @authorize('lm:users:customfields:read')
    @endpoint(api=True)
    def handle_get_custom_fields(self, http_context, user):
        """
        Get custom fields informations from user and prepare it for landingpage

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param user: User login
        :type user: string
        :return: All displayable custom fields informations from user
        :rtype: list
        """

        if user != 'root':
            custom_fields = self.context.schoolmgr.custom_fields
            custom_fields_to_show = []
            profil = AuthenticationService.get(self.context).get_provider().get_profile(user)
            role = profil['sophomorixRole'] + 's'

            for field in ['custom', 'customMulti', 'proxyAddresses']:
                if field not in custom_fields.keys():
                    continue
                if role not in custom_fields[field].keys():
                    continue

                if 'custom' in field:
                    for entry, details in custom_fields[field][role].items():
                        show = details.get('show', False)
                        title = details.get('title', '')
                        editable = details.get('editable', False)
                        if show:
                            attr = f'sophomorixC{field[1:]}{entry}'

                            if 'Multi' in field:
                                value = profil.get(attr, [])
                                # Sophomorix sends a string if there's only one address
                                if isinstance(value, str):
                                    value = [value]
                            else:
                                value = profil.get(attr, '')
                            custom_fields_to_show.append({
                                'attr': attr,
                                'title': title,
                                'editable': editable,
                                'value': value,
                            })
                else:
                    # Proxyaddresses
                    if custom_fields['proxyAddresses'][role].get('show', False) == True:
                        addresses = profil.get('proxyAddresses', [])
                        # Sophomorix sends a string if there's only one address
                        if isinstance(addresses, str):
                            addresses = [addresses]

                        custom_fields_to_show.append({
                            'attr': 'proxyAddresses',
                            'title': custom_fields['proxyAddresses'][role].get('title', ''),
                            'editable': custom_fields['proxyAddresses'][role].get('editable', False),
                            'value': addresses,
                        })

            return custom_fields_to_show
