import unicodecsv as csv
import os
import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lm_common.api import CSVSpaceStripper
from aj.auth import authorize
from aj.plugins.lm_common.api import lm_backup_file
from aj.plugins.lm_common.api import lmn_getUserSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/users/students')
    @endpoint(api=True)
    def handle_api_students(self, http_context):
        path = '/etc/linuxmuster/sophomorix/default-school/students.csv'
        fieldnames = [
            'class',
            'last_name',
            'first_name',
            'birthday',
        ]
        if http_context.method == 'GET':
            with authorize('lm:users:students:read'):
                return list(
                    csv.DictReader(
                        CSVSpaceStripper(
                            open(path),
                            encoding=http_context.query.get('encoding', 'utf-8')
                        ),
                        delimiter=';',
                        fieldnames=fieldnames
                    )
                )
        if http_context.method == 'POST':
            with authorize('lm:users:students:write'):
                data = http_context.json_body()
                for item in data:
                    item.pop('_isNew', None)
                    item.pop('null', None)
                lm_backup_file(path)
                with open(path, 'w') as f:
                    csv.DictWriter(
                        f,
                        delimiter=';',
                        fieldnames=fieldnames,
                        encoding=http_context.query.get('encoding', 'utf-8')
                    ).writerows(data)

    @url(r'/api/lm/users/teachers')
    @endpoint(api=True)
    def handle_api_teachers(self, http_context):
        path = '/etc/linuxmuster/sophomorix/default-school/teachers.csv'
        fieldnames = [
            'class',
            'last_name',
            'first_name',
            'birthday',
            'login',
            'password',
            'usertoken',
            'quota',
            'mailquota',
            'reserved',
        ]
        if http_context.method == 'GET':
            with authorize('lm:users:teachers:read'):
                return list(
                    csv.DictReader(
                        CSVSpaceStripper(
                            open(path),
                            encoding=http_context.query.get('encoding', 'utf-8')
                        ),
                        delimiter=';',
                        fieldnames=fieldnames
                    )
                )
        if http_context.method == 'POST':
            with authorize('lm:users:teachers:write'):
                data = http_context.json_body()
                for item in data:
                    item.pop('_isNew', None)
                lm_backup_file(path)
                with open(path, 'w') as f:
                    csv.DictWriter(
                        f,
                        delimiter=';',
                        fieldnames=fieldnames,
                        encoding=http_context.query.get('encoding', 'utf-8')
                    ).writerows(data)

    # ATi - temp getting teachers userlist from LDAP. Most likely we switch this to sophomorix
    #@url(r'/api/lm/ldapUsers/teachers')
    #@endpoint(api=True)
    #def handle_api_teachers(self, http_context):
    #    fieldnames = [
    #        'class',
    #        'last_name',
    #        'first_name',
    #        'birthday',
    #        'login',
    #        'password',
    #        'usertoken',
    #        'quota',
    #        'mailquota',
    #        'reserved',
    #    ]
    #    if http_context.method == 'GET':
    #        with authorize('lm:users:teachers:read'):

    #            return list(
    #                csv.DictReader(
    #                    CSVSpaceStripper(
    #                        open(path),
    #                        encoding=http_context.query.get('encoding', 'utf-8')
    #                    ),
    #                    delimiter=';',
    #                    fieldnames=fieldnames
    #                )
    #            )
    #    if http_context.method == 'POST':
    #        with authorize('lm:users:teachers:write'):
    #            data = http_context.json_body()
    #            for item in data:
    #                item.pop('_isNew', None)
    #            lm_backup_file(path)
    #            with open(path, 'w') as f:
    #                csv.DictWriter(
    #                    f,
    #                    delimiter=';',
    #                    fieldnames=fieldnames,
    #                    encoding=http_context.query.get('encoding', 'utf-8')
    #                ).writerows(data)

    @url(r'/api/lm/users/extra-students')
    @endpoint(api=True)
    def handle_api_extra_students(self, http_context):
        path = '/etc/linuxmuster/sophomorix/default-school/extrastudents.csv'
        fieldnames = [
            'class',
            'last_name',
            'first_name',
            'birthday',
            'login',
            'reserved',
        ]
        if http_context.method == 'GET':
            with authorize('lm:users:extra-students:read'):
                return list(
                    csv.DictReader(
                        CSVSpaceStripper(
                            open(path),
                            encoding=http_context.query.get('encoding', 'utf-8')
                        ),
                        delimiter=';',
                        fieldnames=fieldnames
                    )
                )
        if http_context.method == 'POST':
            with authorize('lm:users:extra-students:write'):
                data = http_context.json_body()
                for item in data:
                    item.pop('_isNew', None)
                lm_backup_file(path)
                with open(path, 'w') as f:
                    csv.DictWriter(
                        f,
                        delimiter=';',
                        fieldnames=fieldnames,
                        encoding=http_context.query.get('encoding', 'utf-8')
                    ).writerows(data)

    @url(r'/api/lm/users/extra-courses')
    @endpoint(api=True)
    def handle_api_extra_courses(self, http_context):
        path = '/etc/sophomorix/user/extrakurse.txt'
        fieldnames = [
            'course',
            'base_name',
            'count',
            'birthday',
            'gecos',
            'password',
            'removal_date',
        ]
        if http_context.method == 'GET':
            with authorize('lm:users:extra-courses:read'):
                return list(
                    csv.DictReader(
                        CSVSpaceStripper(
                            open(path),
                            encoding=http_context.query.get('encoding', 'utf-8')
                        ),
                        delimiter=';',
                        fieldnames=fieldnames
                    )
                )
        if http_context.method == 'POST':
            with authorize('lm:users:extra-courses:write'):
                data = http_context.json_body()
                for item in data:
                    item.pop('_isNew', None)
                lm_backup_file(path)
                with open(path, 'w') as f:
                    csv.DictWriter(
                        f,
                        delimiter=';',
                        fieldnames=fieldnames,
                        encoding=http_context.query.get('encoding', 'utf-8')
                    ).writerows(data)

    @url(r'/api/lm/users/check')
    @authorize('lm:users:check')
    @endpoint(api=True)
    def handle_api_users_check(self, http_context):
        #path = '/tmp/sophomorix-check.log'
        #open(path, 'w').close()
        #try:
        #    subprocess.check_call('sophomorix-check > %s' % path, shell=True, env={'LC_ALL': 'C'})
        #except Exception as e:
        #    raise EndpointError(str(e))
        ##jsonS =  subprocess.call('sophomorix-check -j 1>/dev/null', shell=True),
        ##raise Exception(str(jsonS))
        jsonS = subprocess.Popen('sophomorix-check -jj 1>/dev/null',stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  shell=True).stdout.read()
        ## remove everything before the first { to get rid of real error messages in stderr
        jsonS = jsonS[jsonS.find('{'):]
        # json string to dict
        jsonObj = json.loads(jsonS,encoding='latin1')
        ##print jsonObj['SUMMARY'][1]['ADD']['RESULT']
        #raise Exception(str(jsonObj))
        results = {
            'add': [],
            'move': [],
            'kill': [],
            'errors': [],
        #   'report': open('/var/lib/sophomorix/check-result/report.admin').read().decode('utf-8', errors='ignore'),

           }


        #lines = open('/tmp/sophomorix-check.log').read().decode('utf-8', errors='ignore').splitlines()
        #while lines:
        #    l = lines.pop(0)
        #    if 'Fehlerhafter Datensatz' in l:
        #        s = ''
        #        while lines[0][0] != '#':
        #            s += lines[0].strip() + '\n'
        #            lines.pop(0)
        #        results['errors'].append(s)
        #    if 'Looking for tolerated users to be moved/deactivated' in l or 'Looking for users to be tolerated' in l:
        #        while lines[0][0] != '#':
        #            s = lines.pop(0).strip()
        #            if '--->' in s:
        #                results['move'].append(s)
        #    if 'Looking for users to be added' in l:
        #        while lines[0][0] != '#':
        #            results['add'].append(lines.pop(0).strip())
        #    if 'killable users to be killed' in l:
        #        while lines[0][0] != '#':
        #            s = lines.pop(0).strip()
        #            if '--->' in s:
        #                results['kill'].append(s)

        return results

    @url(r'/api/lm/users/apply')
    @authorize('lm:users:apply')
    @endpoint(api=True)
    def handle_api_users_apply(self, http_context):
        path = '/tmp/sophomorix.log'

        open(path, 'w').close()

        script = ''
        if http_context.json_body()['doAdd']:
            script += 'sophomorix-add >> %s;' % path
        if http_context.json_body()['doMove']:
            script += 'sophomorix-move >> %s;' % path
        if http_context.json_body()['doKill']:
            script += 'sophomorix-kill >> %s;' % path

        try:
            subprocess.check_call(script, shell=True, env={'LC_ALL': 'C'})
        except Exception as e:
            raise EndpointError(None, message=str(e))

    @url(r'/api/lm/users/password')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_password(self, http_context):
        action = http_context.json_body()['action']
        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        ## Passwort auslesen
        if action == 'get':
            return lmn_getUserSophomorixValue(user, 'sophomorixFirstPassword')
            #return lmn_getSophomorixValue('sophomorix-user --info -jj', user, '/USERS/'+user+'/sophomorixFirstPassword')
        if action == 'set-initial':
            subprocess.check_call('sophomorix-passwd --set-firstpassword -u %s' % user, shell=True)
        if action == 'set-random':
            subprocess.check_call('sophomorix-passwd -u %s --random' % user, shell=True)
            # alter code mit ausgabe des Passwords
            #r = []
            #for l in subprocess.check_output('sophomorix-passwd -u %s --random' % user, shell=True).splitlines():
            #    if 'Setting password' in l:
            #        r.append({
            #            'user': l.split()[4],
            #            'password': l.split()[-1],
            #        })
            #return r
        if action == 'set':
            subprocess.check_call('sophomorix-passwd -u %s --pass "%s"' % (user, http_context.json_body()['password']), shell=True)

    @url(r'/api/lm/users/print')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_print(self, http_context):
        if http_context.method == 'GET':
            return [
                l.split('-->')[-1].strip()
                for l in subprocess.check_output('sophomorix-print --info', shell=True).splitlines()
                if '-->' in l
            ]
        if http_context.method == 'POST':
            data = http_context.json_body()
            cmd = 'sophomorix-print'
            if data['recent'] is None:
                cmd += ' -a'
            else:
                cmd += ' --back-in-time %s' % data['recent']
            if data['one_per_page']:
                cmd += ' --one-per-page'
            subprocess.check_call(cmd, shell=True)

    @url(r'/api/lm/users/print-download/(?P<name>.+)')
    @authorize('lm:users:passwords')
    @endpoint(api=False, page=True)
    def handle_api_users_print_download(self, http_context, name):
        root = '/var/lib/sophomorix/print-data/'
        path = os.path.abspath(os.path.join(root, name))

        if not path.startswith(root):
            return http_context.respond_forbidden()

        return http_context.file(path, inline=False, name=name)
