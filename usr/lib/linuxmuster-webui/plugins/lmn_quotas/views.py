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
            students = {}
            teachers = {}
            sophomorixCommand = ['sophomorix-quota', '-i', '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'QUOTA/USERS')
            for login, values in result.items():
                # Assuming the values are int ... bad idea
                tmpDict = {
                        'DEFLT':int(values['SHARES']['default-school']['CALC']),
                        'CQ':int(values['CLOUDQUOTA']['CALC_MB']),
                        'GLOBAL':int(values['SHARES']['linuxmuster-global']['CALC']),
                        'MQ':int(values['MAILQUOTA']['CALC']),
                        'displayName':' '.join(reversed(values['MAIL']['displayName'].split()))
                        }
                if values['sophomorixRole'] == 'student':
                    students[login] = tmpDict
                else:
                    teachers[login] = tmpDict
            return [students,teachers]

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
        login = http_context.query['login']
        sophomorixCommand = ['sophomorix-query', '--sam', login, '-jj']
        return lmn_getSophomorixValue(sophomorixCommand, 'USER/'+login)

    @url(r'/api/lm/quotas/apply')
    @authorize('lm:quotas:apply')
    @endpoint(api=True)
    def handle_api_apply(self, http_context):
        try:
            subprocess.check_call('sophomorix-quota > /tmp/apply-sophomorix.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))
