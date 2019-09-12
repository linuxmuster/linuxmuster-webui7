import unicodecsv as csv
import os
import subprocess
import magic
import io

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.api import CSVSpaceStripper
from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_checkPermission, lmn_write_csv, lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/sophomorixUsers/import-list')
    @endpoint(api=True)
    def handle_api_filelistImport(self, http_context):
        def findIndex(lst, key, value):
            for i, dic in enumerate(lst):
                # try catches if dic[key] exists, if it is an unused coloumn this is not the case
                try:
                    if dic[key]:
                        if dic[key] == value:
                            return i
                except Exception:
                    pass
            return -1

        action = http_context.json_body()['action']
        userlist = http_context.json_body()['userlist']

        if action == 'save':
            csvDict = http_context.json_body()['data']
            nElements = (len(csvDict[0]['data']))

            sortedCSV = '/tmp/sortedCSV.csv'
            if os.path.exists(sortedCSV):
                os.remove(sortedCSV)
            # write CSV
            with open(sortedCSV, 'a') as fileToWrite:
                i = 0
                if userlist == 'teachers.csv':
                    while i < nElements:
                        fileToWrite.write('Lehrer;')
                        fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'lastname')]['data'][i]+';')
                        fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'firstname')]['data'][i]+';')
                        fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'birthday')]['data'][i]+';')
                        fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'login')]['data'][i]+';')
                        if findIndex(csvDict, 'coloumn', 'password') != -1:
                            fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'password')]['data'][i]+';')
                        fileToWrite.write('\n')
                        i += 1
                if userlist == 'students.csv':
                    while i < nElements:
                        fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'class')]['data'][i]+';')
                        fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'lastname')]['data'][i]+';')
                        fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'firstname')]['data'][i]+';')
                        fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'birthday')]['data'][i]+';')
                        if findIndex(csvDict, 'coloumn', 'id') != -1:
                            fileToWrite.write(csvDict[findIndex(csvDict, 'coloumn', 'id')]['data'][i]+';')
                        fileToWrite.write('\n')
                        i += 1

            if userlist == 'teachers.csv':
                with authorize('lm:users:teachers:write'):
                    sophomorixCommand = ['sophomorix-newfile', sortedCSV, '--name', userlist, '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                    if result['TYPE'] == "ERROR":
                        return ["ERROR", result['MESSAGE_EN']]
                    if result['TYPE'] == "LOG":
                        return ["LOG", result['LOG']]

            if userlist == 'students.csv':
                with authorize('lm:users:students:write'):
                    sophomorixCommand = ['sophomorix-newfile', sortedCSV, '--name', userlist, '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                    if result['TYPE'] == "ERROR":
                        return ["ERROR", result['MESSAGE_EN']]
                    if result['TYPE'] == "LOG":
                        return ["LOG", result['LOG']]

            return 0

        if action == 'get':
            importList = http_context.json_body()['path']

            if os.path.isfile(importList) is False:
                os.mknod(importList)

            coloumns = []
            # determine encoding
            m = magic.Magic(mime_encoding=True)
            f = open(importList, 'r')
            encoding = m.from_file(importList)

            # Convert this encoding to utf-8
            with io.open(importList, 'r', encoding=encoding) as f:
                text = f.read()
            with io.open(importList, 'w', encoding='utf-8') as f:
                f.write(text)
            f.close
            f = open(importList, 'r')
            reader = csv.reader(f, delimiter=';', encoding=http_context.query.get('encoding', 'utf-8'))
            # determine number of coloumns in csv
            ncol = len(next(reader))
            f.seek(0)
            i = 0
            # create dict entry for every coloumn
            while i < ncol:
                coloumns.append({'coloumn': i})
                i += 1

            # fill coloumn objects with data
            for row in reader:
                i = 0
                while i < ncol:
                    if 'data' in coloumns[i]:
                        coloumns[i]['data'].append(row[i])
                    else:
                        coloumns[i].update({'data': [row[i]]})
                    i += 1

            if http_context.method == 'POST':
                with authorize('lm:users:students:read'):
                    return (coloumns)

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
            'id'
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
                lmn_write_csv(path, fieldnames, data, http_context.query.get('encoding', 'utf-8'))

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
                lmn_write_csv(path, fieldnames, data, http_context.query.get('encoding', 'utf-8'))

    @url(r'/api/lm/sophomorixUsers/teachers')
    @endpoint(api=True)
    def handle_api_sophomorix_teachers(self, http_context):
        action = http_context.json_body()['action']
        if http_context.method == 'POST':
            schoolname = 'default-school'
            teachersList = []

            if action == 'get-all':
                with authorize('lm:users:teachers:read'):
                    # TODO: This could run with --user-basic but not all memberOf are filled. Needs verification
                    sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-basic', '-jj']
            elif action == 'get-list':
                with authorize('lm:users:teachers:list'):
                    # TODO: This could run with --user-basic but not all memberOf are filled. Needs verification
                    # Not so pretty to list teachers, --user-minimal with JSON output would be better
                    sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-basic', '-jj']
            else:
                with authorize('lm:users:teachers:read'):
                    user = http_context.json_body()['user']
                    sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-full', '-jj', '--sam', user]
            teachersCheck = lmn_getSophomorixValue(sophomorixCommand, 'LISTS/USER')
            if len(teachersCheck) != 0:
                teachers = lmn_getSophomorixValue(sophomorixCommand, 'USER')
                for teacher in teachers:
                    teachersList.append(teachers[teacher])
                return teachersList
            else:
                return ["none"]

    @url(r'/api/lm/sophomorixUsers/students')
    @endpoint(api=True)
    def handle_api_sophomorix_students(self, http_context):
        action = http_context.json_body()['action']
        if http_context.method == 'POST':
            schoolname = 'default-school'
            studentsList = []
            with authorize('lm:users:students:read'):
                if action == 'get-all':
                    sophomorixCommand = ['sophomorix-query', '--student', '--schoolbase', schoolname, '--user-basic', '-jj']
                else:
                    user = http_context.json_body()['user']
                    # sophomorixCommand = ['sophomorix-query', '--student', '--schoolbase', schoolname, '--user-full', '-jj', '--sam', user]
                    sophomorixCommand = ['sophomorix-query', '--user-full', '-jj', '--sam', user]
                studentsCheck = lmn_getSophomorixValue(sophomorixCommand, 'LISTS/USER')
                if len(studentsCheck) != 0:
                    students = lmn_getSophomorixValue(sophomorixCommand, 'USER')
                    for student in students:
                        # TODO: get a better way to remove Birthay from user detail page
                        students[student]['sophomorixBirthdate'] = 'hidden'
                        studentsList.append(students[student])
                    return studentsList
                else:
                    return ["none"]

    @url(r'/api/lm/sophomorixUsers/schooladmins')
    @endpoint(api=True)
    def handle_api_sophomorix_schooladmins(self, http_context):
        action = http_context.json_body()['action']
        if http_context.method == 'POST':
            schooladminsList = []
            with authorize('lm:users:schooladmins:read'):
                if action == 'get-all':
                    sophomorixCommand = ['sophomorix-query', '--schooladministrator', '--user-full', '-jj']
                else:
                    user = http_context.json_body()['user']
                    sophomorixCommand = ['sophomorix-query', '--schooladministrator', '--user-full', '-jj', '--sam', user]
                schooladminsCheck = lmn_getSophomorixValue(sophomorixCommand, 'LISTS/USER')
                if len(schooladminsCheck) != 0:
                    schooladmins = lmn_getSophomorixValue(sophomorixCommand, 'USER')
                    for schooladmin in schooladmins:
                        schooladminsList.append(schooladmins[schooladmin])
                    return schooladminsList
                else:
                    return ["none"]
        if http_context.method == 'POST':
            with authorize('lm:users:schooladmins:write'):
                return 0

    @url(r'/api/lm/sophomorixUsers/globaladmins')
    @endpoint(api=True)
    def handle_api_sophomorix_globaladmins(self, http_context):
        action = http_context.json_body()['action']
        if http_context.method == 'POST':
            globaladminsList = []
            with authorize('lm:users:globaladmins:read'):
                if action == 'get-all':
                    sophomorixCommand = ['sophomorix-query', '--globaladministrator', '--user-full', '-jj']
                else:
                    user = http_context.json_body()['user']
                    sophomorixCommand = ['sophomorix-query', '--globaladministrator', '--user-full', '-jj', '--sam', user]
                globaladminsCheck = lmn_getSophomorixValue(sophomorixCommand, 'LISTS/USER')
                if len(globaladminsCheck) != 0:
                    globaladmins = lmn_getSophomorixValue(sophomorixCommand, 'USER')
                    for globaladmin in globaladmins:
                        globaladminsList.append(globaladmins[globaladmin])
                    return globaladminsList
                else:
                    return ["none"]
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
                lmn_write_csv(path, fieldnames, data, http_context.query.get('encoding', 'utf-8'))

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
                lmn_write_csv(path, fieldnames, data, http_context.query.get('encoding', 'utf-8'))

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
        # TODO: Update this function for output
        # replace sophomorix-move by sophomorix-update
        open(path, 'w').close()

        script = ''
        if http_context.json_body()['doAdd']:
            script += 'sophomorix-add >> %s;' % path
        if http_context.json_body()['doMove']:
            script += 'sophomorix-update >> %s;' % path
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
        # Read Password
        if action == 'get':
            sophomorixCommand = ['sophomorix-user', '--info', '-jj', '-u', user]
            return lmn_getSophomorixValue(sophomorixCommand, '/USERS/'+user+'/sophomorixFirstPassword')
        if action == 'set-initial':
            sophomorixCommand = ['sophomorix-passwd', '--set-firstpassword', '-jj', '-u', user]
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'set-random':
            sophomorixCommand = ['sophomorix-passwd', '-u', user, '--random', '8', '-jj']
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'set':
            password = http_context.json_body()['password']
            sophomorixCommand = ['sophomorix-passwd', '-u', user, '--pass', password, '-jj']
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'set-actual':
            password = http_context.json_body()['password']
            sophomorixCommand = ['sophomorix-passwd', '-u', user, '--pass', password, '--nofirstpassupdate', '--hide', '-jj']
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')

    @url(r'/api/lm/users/change-school-admin')
    @authorize('lm:users:schooladmins:create')
    @endpoint(api=True)
    def handle_api_users_schooladmins_create(self, http_context):
        school = 'default-school'
        action = http_context.json_body()['action']
        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        if action == 'create':
            with authorize('lm:users:schooladmins:create'):
                sophomorixCommand = ['sophomorix-admin', '--create-school-admin', user, '--school', school, '--random-passwd-save', '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                #if result['TYPE'] == "ERROR":
                #    return ["ERROR", result['MESSAGE_EN']]
                #if result['TYPE'] == "LOG":
                #    return ["LOG", result['LOG']]
                return result['COMMENT_EN']
                ### return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'delete':
            with authorize('lm:users:schooladmins:delete'):
                sophomorixCommand = ['sophomorix-admin', '--kill', user, '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                #if result['TYPE'] == "ERROR":
                #    return ["ERROR", result['MESSAGE_EN']]
                #if result['TYPE'] == "LOG":
                #    return ["LOG", result['LOG']]
                return result['COMMENT_EN']

    @url(r'/api/lm/users/change-global-admin')
    @authorize('lm:users:globaladmins:create')
    @endpoint(api=True)
    def handle_api_users_globaladmins_create(self, http_context):
        action = http_context.json_body()['action']
        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        if action == 'create':
            with authorize('lm:users:globaladmins:create'):
                sophomorixCommand = ['sophomorix-admin', '--create-global-admin', user, '--random-passwd-save', '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                #if result['TYPE'] == "ERROR":
                #    return ["ERROR", result['MESSAGE_EN']]
                #if result['TYPE'] == "LOG":
                #    return ["LOG", result['LOG']]
                return result['COMMENT_EN']
                # return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'delete':
            with authorize('lm:users:globaladmins:delete'):
                sophomorixCommand = ['sophomorix-admin', '--kill', user, '-jj']
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                #if result['TYPE'] == "ERROR":
                #    return result['MESSAGE_EN']
                #if result['TYPE'] == "LOG":
                #    return result['LOG']
                return result['COMMENT_EN']
                # return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')

    #@url(r'/api/lmn/sophomorixUsers/new-file')
    #@endpoint(api=True)
    #def handle_api_sophomorix_newfile(self, http_context):
    #    # TODO needs update for multischool

    #    path = http_context.json_body()['path']
    #    userlist = http_context.json_body()['userlist']
    #    if http_context.method == 'POST':

    #        if userlist == 'teachers.csv':
    #            with authorize('lm:users:teachers:write'):
    #                sophomorixCommand = ['sophomorix-newfile', path, '--name', userlist, '-jj']
    #                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
    #                if result['TYPE'] == "ERROR":
    #                    return ["ERROR", result['MESSAGE_EN']]
    #                if result['TYPE'] == "LOG":
    #                    return ["LOG", result['LOG']]

    #        if userlist == 'students.csv':
    #            with authorize('lm:users:students:write'):
    #                sophomorixCommand = ['sophomorix-newfile', path, '--name', userlist, '-jj']
    #                result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
    #                if result['TYPE'] == "ERROR":
    #                    return ["ERROR", result['MESSAGE_EN']]
    #                if result['TYPE'] == "LOG":
    #                    return ["LOG", result['LOG']]

    @url(r'/api/lm/users/print')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_print(self, http_context):
        school = 'default-school'
        if http_context.method == 'GET':

            sophomorixCommand = ['sophomorix-print', '--school', school, '--info', '-jj']

            with authorize('lm:users:students:read'):
                # classes = lmn_getSophomorixValue(sophomorixCommand, 'LIST_BY_sophomorixSchoolname_sophomorixAdminClass/'+school)
                # Check if there are any classes if not return empty list
                classes_raw = lmn_getSophomorixValue(sophomorixCommand, '')
                if 'LIST_BY_sophomorixSchoolname_sophomorixAdminClass' not in classes_raw:
                    classes = []
                else:
                    classes = classes_raw['LIST_BY_sophomorixSchoolname_sophomorixAdminClass'][school]
                    if lmn_checkPermission({'id': 'lm:users:teachers:read', 'default': False}):
                        # append empty element. This references to all users
                        classes.append('')
                    else:
                        classes.remove('teachers')
                return classes

        if http_context.method == 'POST':
            user = http_context.json_body()['user']
            one_per_page = http_context.json_body()['one_per_page']
            pdflatex = http_context.json_body()['pdflatex']
            schoolclass = http_context.json_body()['schoolclass']
            sophomorixCommand = ['sophomorix-print', '--school', school, '--caller', str(user)]
            if one_per_page:
                sophomorixCommand.extend(['--one-per-page'])
            if pdflatex:
                sophomorixCommand.extend(['--command'])
                sophomorixCommand.extend(['pdflatex'])
            if schoolclass:
                sophomorixCommand.extend(['--class', schoolclass])
            # sophomorix-print needs the json parameter at the very end
            sophomorixCommand.extend(['-jj'])
            # check permissions
            if not schoolclass:
                # double check if user is allowed to print all passwords
                with authorize('lm:users:teachers:read'):
                    pass
            # double check if user is allowed to print teacher passwords
            if schoolclass == 'teachers':
                with authorize('lm:users:teachers:read'):
                    pass
            # generate real shell environment for sophomorix print
            shell_env = {'TERM': 'xterm', 'SHELL': '/bin/bash',  'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',  'HOME': '/root', '_': '/usr/bin/python2'}

            subprocess.check_call(sophomorixCommand, shell=False, env=shell_env)
            return
            # return lmn_getSophomorixValue(sophomorixCommand, 'JSONINFO')

    @url(r'/api/lm/users/print-download/(?P<name>.+)')
    @authorize('lm:users:passwords')
    @endpoint(api=False, page=True)
    def handle_api_users_print_download(self, http_context, name):
        root = '/var/lib/sophomorix/print-data/'
        path = os.path.abspath(os.path.join(root, name))

        if not path.startswith(root):
            return http_context.respond_forbidden()

        return http_context.file(path, inline=False, name=name)

    @url(r'/api/lm/users/test-first-password/(?P<name>.+)')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_print_download(self, http_context, name):
        line = subprocess.check_output(['sophomorix-passwd', '--test-firstpassword', '-u', name]).splitlines()[-4]
        return '1 OK' in line

