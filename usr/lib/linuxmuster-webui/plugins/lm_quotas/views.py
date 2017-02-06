import ldap
import subprocess

from jadi import component
import aj
from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lm_common.api import lm_backup_file


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/quotas')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_quotas(self, http_context):
        path = '/etc/sophomorix/user/quota.txt'
        mpath = '/etc/sophomorix/user/mailquota.txt'
        if http_context.method == 'GET':
            r = {}

            for line in open(path):
                if ':' in line and not line.startswith('#'):
                    k, v = line.split(':', 1)
                    r[k.strip()] = {
                        'home': int(v.split('+')[0].strip()),
                        'var': int(v.split('+')[1].strip()),
                    }

            for line in open(mpath):
                if ':' in line and not line.startswith('#'):
                    k, v = line.split(':', 1)
                    k = k.strip()
                    if k in r:
                        r[k]['mail'] = int(v.strip())

            return r
        if http_context.method == 'POST':
            lm_backup_file(path)
            with open(path, 'w') as f:
                f.write('\n'.join(
                    '%s: %s+%s' % (
                        k, v['home'], v['var'],
                    )
                    for k, v in http_context.json_body().items()
                ))
            lm_backup_file(mpath)
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
            lines = filter(None, lines)
            lines = lines[3:-2]
            return [
                {
                    'name': line.split('|')[0].strip(),
                    'quota': {
                        'home': int(line.split('|')[2].strip().split('+')[0]),
                        'var': int(line.split('|')[2].strip().split('+')[1]),
                    } if line.split('|')[2].strip() else {},
                    'mailquota': int(line.split('|')[3].strip()) if line.split('|')[3].strip() else None,
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
            lines = filter(None, lines)
            lines = lines[3:-3]
            return [
                {
                    'name': line.split('|')[0].strip(),
                    'quota': {
                        'home': int(line.split('|')[1].strip().split('+')[0]),
                        'var': int(line.split('|')[1].strip().split('+')[1]),
                    } if '+' in line and len(line.split('|')[1].strip()) > 1 else {},
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
        params = aj.config.data['linuxmuster']['ldap']
        l = ldap.initialize('ldap://' + params['host'])
        l.bind_s(params['binddn'], params['bindpw'])
        l.set_option(ldap.OPT_REFERRALS, 0)
        users = l.search_s(
            params['searchdn'],
            ldap.SCOPE_SUBTREE,
            '(&(objectClass=posixAccount)(|(cn=*%s*)(uid=*%s*)))' % (
                http_context.query['q'],
                http_context.query['q'],
            ),
            attrlist=['uid', 'cn'],
        )
        return list(users)

    @url(r'/api/lm/quotas/apply')
    @authorize('lm:quotas:apply')
    @endpoint(api=True)
    def handle_api_apply(self, http_context):
        try:
            subprocess.check_call('sophomorix-quota > /tmp/apply-sophomorix.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))
