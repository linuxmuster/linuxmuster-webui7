"""
APIs for user management in linuxmuster.net. Basically parse the output of
sophomorix commands.
"""

import unicodecsv as csv
import os
import subprocess
import magic
import io

from jadi import component
from aj.api.http import get, post, url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import lmn_getSophomorixValue
from aj.plugins.lmn_common.lmnfile import LMNFile


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/custom')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom(self, http_context):
        """
        Update a custom sophomorix field.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            n = http_context.json_body()['index']
            user = http_context.json_body()['user']
            value = http_context.json_body()['value']

            try:
                command = ['sophomorix-user', '-u', user, f'--custom{n}', value, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

    @url(r'/api/lm/custommulti/add')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom_mutli_add(self, http_context):
        """
        Add a sophomorix field in custom multi.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            n = http_context.json_body()['index']
            user = http_context.json_body()['user']
            value = http_context.json_body()['value']

            try:
                command = ['sophomorix-user', '-u', user, f'--add-custom-multi{n}', value, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

    @url(r'/api/lm/custommulti/remove')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom_multi_remove(self, http_context):
        """
        Remove a sophomorix field in custom multi.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            n = http_context.json_body()['index']
            user = http_context.json_body()['user']
            value = http_context.json_body()['value']

            try:
                command = ['sophomorix-user', '-u', user, f'--remove-custom-multi{n}', value, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

    @url(r'/api/lm/setProxyAddresses')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_set_proxy_addresses(self, http_context):
        """
        Set proxyAddresses, e.g. emails, for an user.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            user = http_context.json_body()['user']
            addresses = ','.join(http_context.json_body()['addresses'])

            try:
                command = ['sophomorix-user', '-u', user, '--set-proxy-addresses', addresses, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

    @url(r'/api/lm/changeProxyAddresses')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_set_proxy_addresses(self, http_context):
        """
        Add or remove an email in proxyAddresses, e.g. emails, for an user.
        Method POST.
        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            action = http_context.json_body()['action']

            if action not in ['add', 'remove']:
                raise EndpointError(None)

            user = http_context.json_body()['user']
            address = http_context.json_body()['address']

            try:
                command = ['sophomorix-user', '-u', user, f'--{action}-proxy-addresses', address, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

