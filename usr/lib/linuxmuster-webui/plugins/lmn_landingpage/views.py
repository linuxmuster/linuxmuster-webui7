"""
Module to display a welcome page for the user with useful informations.
"""

# coding=utf-8
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
# from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_getSophomorixValue

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/quota/(?P<user>.+)')
    @endpoint(api=True)
    def handle_api_quota(self, http_context, user):
        """
        Get quota informations from user through sophomorix-query.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param user: User login
        :type user: string
        :return: All quotas informations from user
        :rtype: dict
        """

        if http_context.method == 'GET':

                if user != 'root':
                    sophomorixCommand = ['sophomorix-query', '--sam', user, '--user-full', '--quota-usage', '-jj']
                    jsonpath          = 'USER/' + user
                    return lmn_getSophomorixValue(sophomorixCommand, jsonpath)
                return {}
