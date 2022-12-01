"""
Generate a matrix of permissions and api for all plugins and sidebar items.
"""

import logging
import os
from jadi import component


from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider
from aj.plugins.lmn_common.lmnfile import LMNFile


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

## Check rights
    @get(r'/api/lmn/permissions')
    @authorize('lm:schoolsettings') # TODO : adapt
    @endpoint(api=True)
    def handle_api_get_permissions(self, http_context):
        """
        Get the whole list of plugins, permissions and api.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All plugins details
        :rtype: dict
        """

        # Load all sidebar items and rearrange it in a dict
        # Children are not parsed
        sidebarItems = {}
        for s in SidebarItemProvider.all(self.context):
            for elt in s.provide():
                if elt['attach'] is not None:
                    elt['category'] = elt['attach'].split(':')[1]
                    elt['plugin'] = s.__module__.split('.')[2]
                    sidebarItems[elt['url']] = elt

        apiPermissionDict = {}
        sidebarPermissionDict = {}

        # Load all permissions and sort it
        for p in PermissionProvider.all(self.context):
            for perm in p.provide():
                if perm['id'].startswith('sidebar'):
                    url = perm['id'].split(':')[2]
                    sidebarPermissionDict[url] = {
                        'name': perm['name'],
                        # perm['default'] always True in Ajenti,
                        # but not with lm authenticator
                        'default': False,
                        'plugin': sidebarItems[url]['plugin']
                    }
                else:
                    apiPermissionDict[perm['id']] = {
                        'name': perm['name'],
                        # perm['default'] may be True in Ajenti,
                        # but not with lm authenticator
                        'default': False,
                    }

        def filter_url_regexp(url):
            """
            Remove all regexp pattern from URL.

            :param url: URL Regexp
            :type url: string
            :return: Proper URL
            :rtype: string
            """

            return url.replace('(?P', '').replace('.+)', '').replace('\w+)', '')

        def get_provider(url):
            """
            Extract plugin provider from the url pattern.

            :param s: Url pattern
            :return: Provider
            :rtype: string
            """

            if '/lm' in url.pattern:
                return 'Linuxmuster.net'
            if '/ni' in url.pattern:
                return 'Netzint'
            return 'Ajenti'

        PluginDict = {}

        for plugin in HttpPlugin.all(self.context):
            # Split aj.plugins.network.views or aj.plugins.core.views.api
            module_split_path = plugin.__class__.__module__.split('.')
            module = module_split_path[-1]
            name = module_split_path[2]

            if len(module_split_path) == 5:
                name = f'{name}-{module}'

            if name not in PluginDict.keys():
                PluginDict[name] = {
                    'methods':{},
                    'lmn':[],
                }

            for n,m in plugin.__class__.__dict__.items():
                if hasattr(m, 'url_pattern'):
                    PluginDict[name]['provider'] = get_provider(m.url_pattern)

                    permission_id = None
                    if hasattr(m, 'permission_id'):
                        permission_id = m.permission_id

                    api, auth, page = '', '', ''
                    doc = m.__doc__

                    if hasattr(m, 'api'):
                        api = m.api
                    if hasattr(m, 'auth'):
                        auth = m.auth
                    if hasattr(m, 'page'):
                        page = m.page

                    url = filter_url_regexp(m.url_pattern.pattern[1:-1])
                    details = {
                            'permission_id': permission_id,
                            'doc': doc,
                            'api': api,
                            'auth': auth,
                            'page': page,
                            'method': m.method if hasattr(m, 'method') else 'url'
                        }

                    if url in PluginDict[name]['methods']:
                        PluginDict[name]['methods'][url].append(details)
                    else:
                        PluginDict[name]['methods'][url] = [details]


        ## Load default ui permissions from permissions.yml files
        plugins_path = '/usr/lib/linuxmuster-webui/plugins'

        for plugin in os.listdir(plugins_path):
            path = os.path.join(plugins_path, plugin)
            plugin_permissions = []
            if os.path.isdir(path) and 'lmn_' in plugin:
                perm_path = os.path.join(path, 'permissions.yml')

                lmn_permissions = None
                if os.path.isfile(perm_path):
                    with LMNFile(perm_path, 'r') as f:
                        lmn_permissions = f.data

                if lmn_permissions is not None:
                    permissions = {}
                    for role, perms_list in lmn_permissions.items():
                        permissions[role] = {}
                        for perm in perms_list:
                            cat_id, value = perm.split()
                            # Remove last ":"
                            cat_id = cat_id[:-1]
                            plugin_permissions.append(cat_id)

                            if 'sidebar' in cat_id:
                                url = cat_id.split(':')[-1]

                                if url not in sidebarPermissionDict.keys():
                                    sidebarPermissionDict[url] = {
                                        'name': url,
                                        'default': False,
                                        'plugin': "NOT IMPLEMENTED"

                                    }
                                    logging.warning(f'{url} not listed in PermissionProvider')
                                sidebarPermissionDict[url][role] = value

                            # API permissions
                            else:
                               if cat_id not in apiPermissionDict.keys():
                                    apiPermissionDict[cat_id] = {
                                        'name': "NO DESCRIPTION",
                                        'default': False
                                    }
                                    logging.warning(f'{cat_id} not listed in PermissionProvider')
                               apiPermissionDict[cat_id][role] = value

                # Avoid duplicates
                # We need this later to write per plugin the permissions
                if plugin in PluginDict.keys():
                    PluginDict[plugin]['lmn'] = list(set(plugin_permissions))
                    PluginDict[plugin]['lmn'].sort()

        return PluginDict, apiPermissionDict, sidebarPermissionDict

    @post(r'/api/lmn/permissions/export')
    @authorize('lm:schoolsettings') # TODO : adapt
    @endpoint(api=True)
    def handle_api_export_permissions(self, http_context):
        """
        Export api and sidebar permissions to default ui permissions format.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return:
        :rtype:
        """

        api = http_context.json_body()['api']
        sidebar = http_context.json_body()['sidebar']
        pluginDict = http_context.json_body()['pluginDict']

        plugins_path = '/usr/lib/linuxmuster-webui/plugins'
        roles = [
            'globaladministrator',
            'schooladministrator',
            'teacher',
            'student'
        ]

        for plugin, details in pluginDict.items():
            if len(details['lmn']) > 0:
                permissions = {}

                for role in roles:
                    for permission_id in details['lmn']:
                        if 'sidebar' in permission_id:
                            url = permission_id.split(':')[-1]
                            perm = sidebar[url].get(role, '')
                        else:
                            perm = api[permission_id].get(role, '')

                        if perm:
                            if role not in permissions:
                                permissions[role] = []
                            permissions[role].append(f'{permission_id}: {str(perm).lower()}')

                perm_file = os.path.join(plugins_path, plugin, 'permissions.yml')
                with LMNFile(perm_file, 'w') as f:
                    f.write(permissions)

    # Obsolet
    # @get(r'/api/lmn/permissions/download/(?P<tmpfile>.+)')
    # @authorize('lm:schoolsettings') # TODO : adapt
    # @endpoint(api=False, page=True)
    # def handle_api_download_permissions(self, http_context, tmpfile):
    #     """
    #     Expose default-ui-permissions to download.
    #
    #     :param http_context: HttpContext
    #     :type http_context: HttpContext
    #     :param tmpfile: Path to default-ui-permissions tmp file
    #     :type tmpfile: string
    #     """
    #
    #     if not tmpfile.startswith('/tmp/default-ui-permissions_'):
    #         return
    #
    #     return http_context.file(tmpfile, inline=False, name=tmpfile.encode())


