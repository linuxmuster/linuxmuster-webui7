import unicodecsv as csv
import os
import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lm_common.api import CSVSpaceStripper
from aj.auth import authorize
from aj.plugins.lm_common.api import lm_backup_file
from aj.plugins.lm_common.api import lmn_getSophomorixValue
from aj.plugins.lm_common.api import lmn_genRandomPW



@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/users/students-list')
    @endpoint(api=True)
    def handle_api_students(self, http_context):
        school = 'default-school'
        path = '/etc/linuxmuster/sophomorix/'+school+'/students.csv'
        if os.path.isfile(path) is False:
            os.mknod(path)
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

    @url(r'/api/lm/users/teachers-list')
    @endpoint(api=True)
    def handle_api_teachers(self, http_context):
        school = 'default-school'
        path = '/etc/linuxmuster/sophomorix/'+school+'/teachers.csv'
        if os.path.isfile(path) is False:
            os.mknod(path)
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

    @url(r'/api/lm/sophomorixUsers/teachers')
    @endpoint(api=True)
    def handle_api_sophomorix_teachers(self, http_context):
        if http_context.method == 'GET':
            schoolname = 'default-school'
            teachersList = []
            with authorize('lm:users:teachers:read'):
                sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-full', '-jj']
                teachers = lmn_getSophomorixValue(sophomorixCommand, 'USER')
                for teacher in teachers:
                    teachersList.append(teachers[teacher])
                return teachersList

        if http_context.method == 'POST':
            with authorize('lm:users:teachers:write'):
                return 0

    @url(r'/api/lm/sophomorixUsers/students')
    @endpoint(api=True)
    def handle_api_sophomorix_students(self, http_context):
        if http_context.method == 'GET':
            schoolname = 'default-school'
            studentsList = []
            with authorize('lm:users:students:read'):
                sophomorixCommand = ['sophomorix-query', '--student', '--schoolbase', schoolname, '--user-full', '-jj']
                students = lmn_getSophomorixValue(sophomorixCommand, 'USER')
                for student in students:
                    studentsList.append(students[student])
                return studentsList
        if http_context.method == 'POST':
            with authorize('lm:users:students:write'):
                return 0

    @url(r'/api/lm/sophomorixUsers/schooladmins')
    @endpoint(api=True)
    def handle_api_sophomorix_schooladmins(self, http_context):
        if http_context.method == 'GET':
            schoolname = 'default-school'
            schooladminsList = []
            with authorize('lm:users:schooladmins:read'):
                sophomorixCommand = ['sophomorix-query', '--schooladministrator', '--user-full', '-jj']
                schooladmins = lmn_getSophomorixValue(sophomorixCommand, 'USER', True)
                for schooladmin in schooladmins:
                    schooladminsList.append(schooladmins[schooladmin])
                return schooladminsList
        if http_context.method == 'POST':
            with authorize('lm:users:schooladmins:write'):
                return 0

    @url(r'/api/lm/sophomorixUsers/globaladmins')
    @endpoint(api=True)
    def handle_api_sophomorix_globaladmins(self, http_context):
        if http_context.method == 'GET':
            schoolname = 'default-school'
            globaladminsList = []
            with authorize('lm:users:globaladmins:read'):
                sophomorixCommand = ['sophomorix-query', '--globaladministrator', '--user-full', '-jj']
                globaladmins = lmn_getSophomorixValue(sophomorixCommand, 'USER')
                for globaladmin in globaladmins:
                    globaladminsList.append(globaladmins[globaladmin])
                return globaladminsList
        if http_context.method == 'POST':
            with authorize('lm:users:globaladmins:write'):
                return 0

    @url(r'/api/lm/users/extra-students')
    @endpoint(api=True)
    def handle_api_extra_students(self, http_context):
        school = 'default-school'
        path = '/etc/linuxmuster/sophomorix/'+school+'/extrastudents.csv'
        if os.path.isfile(path) is False:
            os.mknod(path)
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
        school = 'default-school'
        path = '/etc/linuxmuster/sophomorix/'+school+'/extraclasses.csv'
        if os.path.isfile(path) is False:
            os.mknod(path)
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
        sophomorixCommand = ['sophomorix-check', '-jj']
        results = lmn_getSophomorixValue(sophomorixCommand, '')
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
        user = http_context.json_body()['user']
        # Read Password
        if action == 'get':
            sophomorixCommand = ['sophomorix-user', '--info', '-jj', '-u', user]
            return lmn_getSophomorixValue(sophomorixCommand, '/USERS/'+user+'/sophomorixFirstPassword')
        if action == 'set-initial':
            sophomorixCommand = ['sophomorix-passwd', '--set-firstpassword', '-jj', '-u', user]
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'set-random':
            password = lmn_genRandomPW()
            sophomorixCommand = ['sophomorix-passwd', '-u', user, '--pass', password, '-jj']
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'set':
            password = http_context.json_body()['password']
            sophomorixCommand = ['sophomorix-passwd', '-u', user, '--pass', password, '-jj']
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')

    @url(r'/api/lm/users/print')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_print(self, http_context):
        school = 'default-school'
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
                cmd += ' --school ' + school
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
