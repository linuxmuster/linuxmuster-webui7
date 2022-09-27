"""
Module to display a welcome page for the user with useful informations.
"""

from jadi import component
from aj.api.http import get, HttpPlugin
from aj.api.endpoint import endpoint
# from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_getSophomorixValue
from aj.auth import AuthenticationService

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/custom_fields/(?P<user>.+)')
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
