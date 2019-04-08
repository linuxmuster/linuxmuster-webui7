import ldap
import subprocess

from jadi import component
import aj
from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.api import lmn_backup_file, lmconfig, lmn_getSophomorixValue

# Fix user quota : 
    # sophomorix-user --quota linuxmuster-global:500:bla -u de
    # sophomorix-quota -u de
# Call all quotas :
    # sophomorix-quota -n ( no -jj ? )

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/quotas')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_quotas(self, http_context):
        if http_context.method == 'GET':
            lines = subprocess.check_output(['sophomorix-quota', '-i']).splitlines()
            lines = [l for l in lines if l.startswith("|")]
            lines = lines[1:]
            quotas = [{}, {}] # Students, teachers
            for line in lines:
                name       = line.split('|')[1].strip().split('(')[0]
                quota_type = line.split('|')[2].strip().strip("*")
                value      = int(line.split('|')[3].strip()) ## TEST INT
                if 'teacher' in line:
                    if name not in quotas[1]:
                        quotas[1][name] = {}
                    
                    quotas[1][name][quota_type] = value
                else:
                    if name not in quotas[0]:
                        quotas[0][name] = {}
                    
                    quotas[0][name][quota_type] = value
            return quotas
        if http_context.method == 'POST':
            lmn_backup_file(path)
            with open(path, 'w') as f:
                f.write('\n'.join(
                    '%s: %s+%s' % (
                        k, v['home'], v['var'],
                    )
                    for k, v in http_context.json_body().items()
                ))
            lmn_backup_file(mpath)
            with open(mpath, 'w') as f:
                f.write('\n'.join(
                    '%s: %s' % (
                        k, v['mail'],
                    )
                    for k, v in http_context.json_body().items()
                    if v.get('mail', None)
                ))

    @url(r'/api/lm/class-quotas')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_class_quotas(self, http_context):
        if http_context.method == 'GET':
            lines = subprocess.check_output(['sophomorix-class', '-i']).splitlines()
            lines = [l for l in lines if l.startswith("|")]
            lines = lines[1:-1]
            return [
                {
                    'name': line.split('|')[1].strip(),
                    'quota': 0 if '-' in line else int(line.split('|')[4].strip()), 
                    'mailquota': 0 if '-' in line else int(line.split('|')[5].strip()), 
                }
                for line in lines
            ]
        if http_context.method == 'POST':
            for cls in http_context.json_body():
                if cls['quota']['home']:
                    subprocess.check_call(['sophomorix-class', '-c', cls['name'], '--quota', '%s+%s' % (cls['quota']['home'], cls['quota']['var'])])
                if cls['mailquota']:
                    subprocess.check_call(['sophomorix-class', '-c', cls['name'], '--mailquota', cls['mailquota']])

    @url(r'/api/lm/project-quotas')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_project_quotas(self, http_context):
        if http_context.method == 'GET':
            lines = subprocess.check_output(['sophomorix-project', '-i']).splitlines()
            lines = [l for l in lines if l.startswith("|")]
            lines = lines[1:-1]
            return [
                {
                    'name': line.split('|')[1].strip(),
                    'quota': 0 if '-' in line else int(line.split('|')[2].strip()),
                    'mailquota': 0 if '-' in line else int(line.split('|')[3].strip()),
                }
                for line in lines
            ]
        if http_context.method == 'POST':
            for project in http_context.json_body():
                if project['quota']['home']:
                    subprocess.check_call(['sophomorix-project', '-c', project['name'], '--addquota', '%s+%s' % (project['quota']['home'], project['quota']['var'])])

    @url(r'/api/lm/ldap-search')
    @authorize('lm:quotas:ldap-search')
    @endpoint(api=True)
    def handle_api_ldap_search(self, http_context):
        params = lmconfig.data['linuxmuster']['ldap']
        l = ldap.initialize('ldap://' + params['host'])
        l.bind_s(params['binddn'], params['bindpw'])
        l.set_option(ldap.OPT_REFERRALS, 0)
        users = l.search_s(
            params['searchdn'],
            ldap.SCOPE_SUBTREE,
            '(&(objectClass=person)(|(cn=*%s*)(uid=*%s*)))' % (
                http_context.query['q'],
                http_context.query['q'],
            ),
            attrlist=['sn', 'givenName'],
        )
        return [u for u in users if isinstance(u[0], str)]

    @url(r'/api/lm/quotas/apply')
    @authorize('lm:quotas:apply')
    @endpoint(api=True)
    def handle_api_apply(self, http_context):
        try:
            subprocess.check_call('sophomorix-quota > /tmp/apply-sophomorix.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))
