"""
Authentication module for linuxmuster.net that enable and manage LDAP auth.
"""

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import AuthenticationService


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/change-password')
    @endpoint(api=True)
    def handle_api_change_password(self, http_context):
        """
        Change user password through authentication provider.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        provider = AuthenticationService.get(self.context).get_provider()
        try:
            provider.change_password(
                self.context.identity,
                http_context.json_body()['password'],
                http_context.json_body()['new_password']
            )
        except Exception as e:
            raise EndpointError(None, str(e))

