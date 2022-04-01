"""
Module to display a welcome page for the user with useful informations.
"""

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
# from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_getSophomorixValue
from aj.auth import AuthenticationService

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
                    jsonpath = 'USER/' + user
                    return lmn_getSophomorixValue(sophomorixCommand, jsonpath)
                return {}


    @url(r'/api/lmn/custom_fields/(?P<user>.+)')
    @endpoint(api=True)
    def handle_api_custom_fields(self, http_context, user):
        """
        Get custom fields informations from user.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param user: User login
        :type user: string
        :return: All displayable custom fields informations from user
        :rtype: list
        """

        if http_context.method == 'GET':

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
                                    default_value = []
                                else:
                                    default_value = ''
                                custom_fields_to_show.append({
                                    'attr': attr,
                                    'title': title,
                                    'editable': editable,
                                    'value': profil.get(attr, default_value),
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
                                'title': custom_fields['proxyAddresses'][role]['title'],
                                'editable': custom_fields['proxyAddresses'][role]['editable'],
                                'value': addresses,
                            })

                return custom_fields_to_show
