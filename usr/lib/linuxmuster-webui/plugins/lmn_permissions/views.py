"""
Generate a matrix of permissions and api for all plugins and sidebar items.
"""

import logging
import re
from jadi import component


from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

## Check rights
    @url(r'/api/permissions')
    @endpoint(api=True)
    def handle_api_get_permissions(self, http_context):
        """
        Get the whole list of plugins, permissions and api.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All plugins details
        :rtype: dict
        """

        if http_context.method == 'GET':

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
                            'default': perm['default'],
                            'plugin': sidebarItems[url]['plugin']
                        }
                    else:
                        apiPermissionDict[perm['id']] = {
                            'name': perm['name'],
                            'default': perm['default']
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
                # Split aj.plugins.network.views
                name, module = plugin.__class__.__module__.split('.')[-2:]

                if 'core' in plugin.__class__.__module__ :
                    name = 'core-' + module

                if name not in PluginDict.keys():
                    PluginDict[name] = {
                        'methods':{},
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

                        PluginDict[name]['methods'][n] = {
                            'url': filter_url_regexp(m.url_pattern.pattern[1:-1]),
                            'permission_id': permission_id,
                            'doc': doc,
                            'api': api,
                            'auth': auth,
                            'page': page,
                            'post': "Method POST" in doc if doc else ''
                        }

            ## Load default ui permissions from file
            path = '/usr/lib/linuxmuster-webui/etc/default-ui-permissions.ini'

            with open(path, 'r') as f:
                for line in f:
                    # Stanza header
                    if line.startswith('['):
                        role = re.sub(r"[^A-Za-z]+", '', line) ## .strip(']') does not work

                    # Property
                    elif "WEBUI" in line:
                        line = line.split('=')[1].split(':')
                        default = line[-1].strip()

                        if "sidebar" in line[0]:
                            url = line[2].strip()

                            if url not in sidebarPermissionDict.keys():
                                sidebarPermissionDict[url] = {
                                    'name': url,
                                    'default': False,
                                    'plugin': "NOT IMPLEMENTED"

                                }
                                logging.warning('%s not listed in PermissionProvider', cat_id)
                            sidebarPermissionDict[url][role] = default

                        # API permissions
                        else:
                            cat_id = ':'.join(line[:-1])

                            if cat_id not in apiPermissionDict.keys():
                                apiPermissionDict[cat_id] = {
                                    'name': "NO DESCRIPTION",
                                    'default': False
                                }
                                logging.warning('%s not listed in PermissionProvider', cat_id)
                            apiPermissionDict[cat_id][role] = default
            return PluginDict, apiPermissionDict, sidebarPermissionDict
