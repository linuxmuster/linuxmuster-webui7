import ldap
import subprocess

from jadi import component
import aj
from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.api import lmn_backup_file, lmconfig, lmn_getSophomorixValue
from configparser import ConfigParser

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
        school = 'default-school'
        settings_path = '/etc/linuxmuster/sophomorix/'+school+'/school.conf'

        if http_context.method == 'GET':
            ## Parse csv config file
            config = ConfigParser()
            config.read(settings_path)
            settings = {}
            for section in config.sections():
                settings[section] = {}
                for (key, val) in config.items(section):
                   if val.isdigit():
                      val = int(val)
                   if val == 'no':
                        val = False
                   if val == 'yes':
                        val = True
                   settings[section][key] = val
            print(settings)

            ## Get list of non default quota user, others get the default value
            ## Teachers and students are mixed in the same dict
            non_default = {'teacher':{}, 'student':{}}
            quota_types = {
                'linuxmuster-global':'quota_default_global',
                'default-school':'quota_default_school',
                'CQ':'cloudquota_percentage',
                'MQ':'mailquota_default'
                }
            sophomorixCommand = ['sophomorix-quota', '-i', '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'NONDEFAULT_QUOTA/' + school + '/USER')
            for login, values in result.items():
                role = values['sophomorixRole']
                non_default[role][login] = values
                for share, tag in quota_types.items():
                    if share not in values['QUOTA']:
                        values['QUOTA'][share] = {'VALUE':settings['role.'+role][tag]}
                    else:
                        values['QUOTA'][share]['VALUE'] = int(values['QUOTA'][share]['VALUE'])
            return [non_default, settings]

        if http_context.method == 'POST':
            ## Update quota per user
            pass
            # lmn_backup_file(path)
            # with open(path, 'w') as f:
                # f.write('\n'.join(
                    # '%s: %s+%s' % (
                        # k, v['home'], v['var'],
                    # )
                    # for k, v in http_context.json_body().items()
                # ))
            # lmn_backup_file(mpath)
            # with open(mpath, 'w') as f:
                # f.write('\n'.join(
                    # '%s: %s' % (
                        # k, v['mail'],
                    # )
                    # for k, v in http_context.json_body().items()
                    # if v.get('mail', None)
                # ))

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
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_ldap_search(self, http_context):
        login = http_context.query['login']
        sophomorixCommand = ['sophomorix-query', '--anyname', login+'*', '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, 'USER')
        resultArray = []
        for user, details in result.items():
            resultArray.append(details['sn'] + " " + details['givenName'] + " (" + user + ")")
        return resultArray

    @url(r'/api/lm/quotas/apply')
    @authorize('lm:quotas:apply')
    @endpoint(api=True)
    def handle_api_apply(self, http_context):
        try:
            subprocess.check_call('sophomorix-quota > /tmp/apply-sophomorix.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))

    @url(r'/api/lm/get-all-users')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_get_all_users(self, http_context):
        all_users = {}
        sophomorixCommand = ['sophomorix-query', '--teacher', '--student', '--schooladministrator', '--globaladministrator', '-jj']
        return lmn_getSophomorixValue(sophomorixCommand, 'USER')
