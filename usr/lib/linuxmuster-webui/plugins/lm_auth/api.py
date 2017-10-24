import logging
import ldap
import sys
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

        # get ajenti yaml parameters
        params = aj.config.data['linuxmuster']['ldap']
        searchFilter = "(&(cn=%s)(objectClass=user))" % username

        l = ldap.initialize('ldap://' + params['host'])
        #l.set_option(ldap.OPT_REFERRALS, 0)
        # Binduser bind to the  server
        f = open( '/tmp/debug.log', 'w' )
        try:
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.protocol_version = ldap.VERSION3
            #l.bind_s(params['binddn'], password)
            #text_file = open("Output.txt", "w")
            #text_file.write("test: %s" % username)
            #text_file.close()
            #l.bind_s(params['bindtemplate'] % username, password)
            #l.bind_s('CN=Administrator,CN=Users,DC=linuxmuster,DC=lan','KvwwUTgxvd9x5xzY')
            l.bind_s(params['binddn'],  params['bindpw'] )
            #f.write( params['binddn'] + '\n' + params['bindpw'] )
            # f.write (params['binddn']
            #print params['bindtemplate'] % username
        except Exception as e:
            logging.error(str(e))
            return False

        try:
            res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, searchFilter)
            userDN = res[0][0]
        except ldap.LDAPError, e:
            print e
        l.unbind_s()

        #userbind
        try:
            l = ldap.initialize('ldap://' + params['host'])
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.protocol_version = ldap.VERSION3
            l.bind_s(userDN, password)

        except Exception as e:
            logging.error(str(e))
            return False

       #group = l.search_s(
       #    params['logindn'],
       #    ldap.SCOPE_SUBTREE,
       #    attrlist=['memberUid'],
       #)

       # if len(group) == 0:
       #     raise Exception('Login DN group not found')


        permissions = aj.config.data.get('auth', {}).get('users', {}).get(username, {}).get('permissions', {})
        #f.write( userDN + ' ' + password )
        #f.write( password )
        #f.close()

        return {
                'username': username,
                'password': password,
                'permissions': permissions,
                }

        # if username in group[0][1]['memberUid']:
       #     '''
       #     user = l.search_s(
       #         params['bindtemplate'] % username,
       #         ldap.SCOPE_SUBTREE,
       #         attrlist=['schukorechte'],
       #     )
       #     permissions = None
       #     if 'schukorechte' in user[0][1]:
       #         if len(user[0][1]['schukorechte']) > 0:
       #             permissions = json.loads(user[0][1]['schukorechte'][0])
       #     '''
       #     permissions = aj.config.data.get('auth', {}).get('users', {}).get(username, {}).get('permissions', {})
       #     return {
       #         'username': username,
       #         'password': password,
       #         'permissions': permissions,
       #     }
       # else:
       #     raise Exception('User not in the login group')

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
