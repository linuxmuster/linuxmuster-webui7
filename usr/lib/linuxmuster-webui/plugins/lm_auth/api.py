import logging
import ldap
import subprocess
from jadi import component

import aj
from aj.auth import AuthenticationProvider, OSAuthenticationProvider


@component(AuthenticationProvider)
class LMAuthenticationProvider(AuthenticationProvider):
    id = 'lm'
    name = _('Linux Muster LDAP')

    def __init__(self, context):
        self.context = context

    def authenticate(self, username, password):
        if username == 'root':
            return OSAuthenticationProvider.get(self.context).authenticate(username, password)

        params = aj.config.data['linuxmuster']['ldap']
        l = ldap.initialize('ldap://' + params['host'])
        try:
            l.bind_s(params['bindtemplate'] % username, password)
        except Exception as e:
            logging.error(str(e))
            return False

        l.set_option(ldap.OPT_REFERRALS, 0)
        group = l.search_s(
            params['logindn'],
            ldap.SCOPE_SUBTREE,
            attrlist=['memberUid'],
        )

        if len(group) == 0:
            raise Exception('Login DN group not found')

        if username in group[0][1]['memberUid']:
            '''
            user = l.search_s(
                params['bindtemplate'] % username,
                ldap.SCOPE_SUBTREE,
                attrlist=['schukorechte'],
            )
            permissions = None
            if 'schukorechte' in user[0][1]:
                if len(user[0][1]['schukorechte']) > 0:
                    permissions = json.loads(user[0][1]['schukorechte'][0])
            '''
            permissions = aj.config.data.get('auth', {}).get('users', {}).get(username, {}).get('permissions', {})
            return {
                'username': username,
                'password': password,
                'permissions': permissions,
            }
        else:
            raise Exception('User not in the login group')

    def authorize(self, username, permission):
        if username == 'root':
            return True
        return self.context.session.auth_info['permissions'].get(permission['id'], permission['default'])

    def change_password(self, username, password, new_password):
        if not self.authenticate(username, password):
            raise Exception('Wrong password')
        subprocess.check_call('sophomorix-passwd -u %s --pass "%s"' % (username, new_password), shell=True)

    def get_isolation_uid(self, username):
        return 0

    def get_profile(self, username):
        return {}
