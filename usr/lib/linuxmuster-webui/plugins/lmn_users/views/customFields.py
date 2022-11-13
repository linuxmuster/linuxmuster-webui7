"""
API for custom fields management.
"""

from jadi import component
from aj.api.http import get, post, url, patch, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @post(r'/api/lmn/users/(?P<user>[a-z0-9\-]*)/custom/(?P<index>[1-5])')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom(self, http_context, user, index):
        """
        Update a custom sophomorix field.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        value = http_context.json_body()['value']

        try:
            command = ['sophomorix-user', '-u', user, f'--custom{index}', value, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

    @post(r'/api/lmn/users/(?P<user>[a-z0-9\-]*)/custommulti/(?P<index>[1-5])')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom_mutli_add(self, http_context, user, index):
        """
        Add a sophomorix field in custom multi.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        value = http_context.json_body()['value']

        try:
            command = ['sophomorix-user', '-u', user, f'--add-custom-multi{index}', value, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

    @patch(r'/api/lmn/users/(?P<user>[a-z0-9\-]*)/custommulti/(?P<index>[1-5])')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom_multi_remove(self, http_context, user, index):
        """
        Remove a sophomorix field in custom multi.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        value = http_context.json_body()['value']

        try:
            command = ['sophomorix-user', '-u', user, f'--remove-custom-multi{index}', value, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

    @post(r'/api/lmn/users/(?P<user>[a-z0-9\-]*)/proxyaddresses')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_add_proxy_addresses(self, http_context, user):
        """
        Add an email in proxyAddresses, e.g. emails, for an user.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        address = http_context.json_body()['address']

        try:
            command = ['sophomorix-user', '-u', user, f'--add-proxy-addresses', address, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

    @patch(r'/api/lmn/users/(?P<user>[a-z0-9\-]*)/proxyaddresses')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_remove_proxy_addresses(self, http_context, user):
        """
        Remove an email in proxyAddresses, e.g. emails, for an user.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        address = http_context.json_body()['address']

        try:
            command = ['sophomorix-user', '-u', user, f'--remove-proxy-addresses',
                       address, '-jj']
            result = lmn_getSophomorixValue(command, '')
        except IndexError:
            # No error output from sophomorix yet
            raise EndpointError(None)

