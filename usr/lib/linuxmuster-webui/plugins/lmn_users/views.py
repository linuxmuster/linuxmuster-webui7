"""
APIs for user management in linuxmuster.net. Basically parse the output of
sophomorix commands.
"""

import unicodecsv as csv
import os
import subprocess
import magic
import io

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize
from aj.plugins.lmn_common.api import lmn_getSophomorixValue
from aj.plugins.lmn_common.lmnfile import LMNFile
import logging



@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.userStatus = {
        'A' : {'tag':'Activated', 'color':'success'},
        'U' : {'tag':'Usable', 'color':'success'},
        'P' : {'tag':'Permanent', 'color':'success'},
        'E' : {'tag':'Enabled', 'color':'success'},
        'S' : {'tag':'Self-activated', 'color':'success'},
        'T' : {'tag':'Tolerated', 'color':'info'},
        'L' : {'tag':'Locked', 'color':'warning'},
        'D' : {'tag':'Deactivated', 'color':'warning'},
        'F' : {'tag':'Frozen', 'color':'warning'},
        'R' : {'tag':'Removable', 'color':'danger'},
        'K' : {'tag':'Killable', 'color':'danger'},
        'X' : {'tag':'Exam', 'color':'danger'},
        'M' : {'tag':'Managed', 'color': 'info'},
    }

    @url(r'/api/lmn/sophomorixUsers/import-list')
    @endpoint(api=True)
    def handle_api_filelistImport(self, http_context):
        """
        Import and save users's import lists (teachers, students, ...).
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Users lists in import mode, one dict per user
        :rtype: list of dict in import mode
        """

        def findIndex(lst, key, value):
            """
            Try catches if dic[key] exists, if it is an unused coloumn this is
            not the case

            :param lst: List to parse
            :type lst: list
            :param key: Key to search
            :type key: string
            :param value: Value to test
            :type value: can be a dict, list or string
            :return: Index of he key or -1
            :rtype: integer
            """

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
            school = self.context.schoolmgr.school 
            if userlist == 'teachers.csv':
                with authorize('lm:users:teachers:write'):
                    if school == 'default-school':
                        sophomorixCommand = ['sophomorix-newfile', sortedCSV, '--name', userlist, '-jj']
                    else:
                        sophomorixCommand = ['sophomorix-newfile', sortedCSV, '--name', school+'.'+userlist, '-jj']
                    result = lmn_getSophomorixValue(sophomorixCommand, 'OUTPUT/0')
                    if result['TYPE'] == "ERROR":
                        return ["ERROR", result['MESSAGE_EN']]
                    if result['TYPE'] == "LOG":
                        return ["LOG", result['LOG']]

            if userlist == 'students.csv':
                with authorize('lm:users:students:write'):
                    if school == 'default-school':
                        sophomorixCommand = ['sophomorix-newfile', sortedCSV, '--name', userlist, '-jj']
                    else:
                        sophomorixCommand = ['sophomorix-newfile', sortedCSV, '--name', school+'.'+userlist, '-jj']
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
            if encoding == "binary":
                # Probably empty file, does it have sense to continue ?
                encoding = 'utf-8'

            # Convert this encoding to utf-8
            with io.open(importList, 'r', encoding=encoding) as f:
                text = f.read()
            with io.open(importList, 'w', encoding='utf-8') as f:
                f.write(text)
            f.close
            f = open(importList, 'rb')
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
        """
        Read and write students csv lists.
        Method GET: read students list.
        Method POST: write students list.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of students in read mode, one dict per student.
        :rtype: list of dict
        """

        path = f'{self.context.schoolmgr.configpath}students.csv'

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
                with LMNFile(path, 'r', fieldnames=fieldnames) as students:
                    return students.read()

        if http_context.method == 'POST':
            with authorize('lm:users:students:write'):
                data = http_context.json_body()
                for item in data:
                    item.pop('_isNew', None)
                    item.pop('null', None)
                with LMNFile(path, 'w', fieldnames=fieldnames) as f:
                    f.write(data)

    @url(r'/api/lm/users/teachers-list')
    @endpoint(api=True)
    def handle_api_teachers(self, http_context):
        """
        Read and write teachers csv lists.
        Method GET: read teachers list.
        Method POST: write teachers list.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of teachers in read mode, one dict per teacher.
        :rtype: list of dict
        """

        path = f'{self.context.schoolmgr.configpath}teachers.csv'

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
                with LMNFile(path, 'r', fieldnames=fieldnames) as teachers:
                    return teachers.read()

        if http_context.method == 'POST':
            with authorize('lm:users:teachers:write'):
                data = http_context.json_body()
                for item in data:
                    item.pop('_isNew', None)
                with LMNFile(path, 'w', fieldnames=fieldnames) as f:
                    f.write(data)

    @url(r'/api/lm/sophomorixUsers/teachers')
    @endpoint(api=True)
    def handle_api_sophomorix_teachers(self, http_context):
        """
        Get teachers list from LDAP tree.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of teachers with details, one teacher per dict.
        :rtype: list of dict
        """

        action = http_context.json_body()['action']
        if http_context.method == 'POST':
            schoolname = self.context.schoolmgr.school
            teachersList = []

            if action == 'get-all':
                with authorize('lm:users:teachers:read'):
                    # TODO: This could run with --user-basic but not all memberOf are filled. Needs verification
                    sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-full', '-jj']
            else:
                with authorize('lm:users:teachers:read'):
                    user = http_context.json_body()['user']
                    sophomorixCommand = ['sophomorix-query', '--teacher', '--schoolbase', schoolname, '--user-full', '-jj', '--sam', user]
            result = lmn_getSophomorixValue(sophomorixCommand, '')
            if 'USER' in result.keys():
                teachers = result['USER']
                for _, details in teachers.items():
                    if details['sophomorixStatus'] in self.userStatus.keys():
                        details['sophomorixStatus'] = self.userStatus[details['sophomorixStatus']]
                    else:
                        details['sophomorixStatus'] = {'tag': details['sophomorixStatus'], 'color': 'default'}
                    details['selected'] = False
                    teachersList.append(details)
                return teachersList
            return ["none"]

    @url(r'/api/lm/sophomorixUsers/students')
    @endpoint(api=True)
    def handle_api_sophomorix_students(self, http_context):
        """
        Get students list from LDAP tree.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of students with details, one student per dict.
        :rtype: list of dict
        """

        action = http_context.json_body()['action']
        if http_context.method == 'POST':
            schoolname = self.context.schoolmgr.school

            studentsList = []
            with authorize('lm:users:students:read'):
                if action == 'get-all':
                    sophomorixCommand = ['sophomorix-query', '--student', '--schoolbase', schoolname, '--user-full', '-jj']
                else:
                    user = http_context.json_body()['user']
                    # sophomorixCommand = ['sophomorix-query', '--student', '--schoolbase', schoolname, '--user-full', '-jj', '--sam', user]
                    sophomorixCommand = ['sophomorix-query', '--user-full', '-jj', '--sam', user]
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                if 'USER' in result.keys():
                    students = result['USER']
                    for _, details in students.items():
                        # TODO: get a better way to remove Birthay from user detail page
                        details['sophomorixBirthdate'] = 'hidden'
                        if details['sophomorixStatus'] in self.userStatus.keys():
                            details['sophomorixStatus'] = self.userStatus[details['sophomorixStatus']]
                        else:
                            details['sophomorixStatus'] = {'tag': details['sophomorixStatus'], 'color': 'default'}
                        details['selected'] = False
                        studentsList.append(details)
                    return studentsList
                return ["none"]

    @url(r'/api/lm/sophomorixUsers/schooladmins')
    @endpoint(api=True)
    def handle_api_sophomorix_schooladmins(self, http_context):
        """
        Get schooladmins list from LDAP tree.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of schooladminss with details, one schooladmin per dict.
        :rtype: list of dict
        """

        if http_context.method == 'POST':
            action = http_context.json_body()['action']
            schooladminsList = []
            with authorize('lm:users:schooladmins:read'):
                if action == 'get-all':
                    sophomorixCommand = ['sophomorix-query', '--schooladministrator', '--user-full', '-jj']
                else:
                    user = http_context.json_body()['user']
                    sophomorixCommand = ['sophomorix-query', '--schooladministrator', '--user-full', '-jj', '--sam', user]
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                if 'USER' in result.keys():
                    schooladmins = result['USER']
                    for _, details in schooladmins.items():
                        details['selected'] = False
                        schooladminsList.append(details)
                    return schooladminsList
                return ["none"]

    @url(r'/api/lm/sophomorixUsers/globaladmins')
    @endpoint(api=True)
    def handle_api_sophomorix_globaladmins(self, http_context):
        """
        Get globaladmins list from LDAP tree.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of globaladminss with details, one globaladmin per dict.
        :rtype: list of dict
        """

        if http_context.method == 'POST':
            action = http_context.json_body()['action']
            globaladminsList = []
            with authorize('lm:users:globaladmins:read'):
                if action == 'get-all':
                    sophomorixCommand = ['sophomorix-query', '--globaladministrator', '--user-full', '-jj']
                else:
                    user = http_context.json_body()['user']
                    sophomorixCommand = ['sophomorix-query', '--globaladministrator', '--user-full', '-jj', '--sam', user]
                result = lmn_getSophomorixValue(sophomorixCommand, '')
                if 'USER' in result.keys():
                    globaladmins = result['USER']
                    for _, details in globaladmins.items():
                        details['selected'] = False
                        globaladminsList.append(details)
                    return globaladminsList
                return ["none"]

    @url(r'/api/lm/users/extra-students')
    @endpoint(api=True)
    def handle_api_extra_students(self, http_context):
        """
        Read and write extra-students csv lists.
        Method GET: read extra-students list.
        Method POST: write extra-students list.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of extra-students in read mode, one dict per extra-student.
        :rtype: list of dict
        """

        path = f'{self.context.schoolmgr.configpath}extrastudents.csv'

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
                with LMNFile(path, 'r', fieldnames=fieldnames) as extra_students:
                    return extra_students.read()

        if http_context.method == 'POST':
            with authorize('lm:users:extra-students:write'):
                data = http_context.json_body()
                for item in data:
                    item.pop('_isNew', None)
                with LMNFile(path, 'w', fieldnames=fieldnames) as f:
                    f.write(data)

    @url(r'/api/lm/users/extra-courses')
    @endpoint(api=True)
    def handle_api_extra_courses(self, http_context):
        """
        Read and write extra-courses csv lists.
        Method GET: read extra-courses list.
        Method POST: write extra-courses list.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of extra-courses in read mode, one dict per extra-course.
        :rtype: list of dict
        """

        path = f'{self.context.schoolmgr.configpath}extraclasses.csv'

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
                with LMNFile(path, 'r', fieldnames=fieldnames) as extra_courses:
                    return extra_courses.read()

        if http_context.method == 'POST':
            with authorize('lm:users:extra-courses:write'):
                data = http_context.json_body()
                for item in data:
                    item.pop('_isNew', None)
                with LMNFile(path, 'w', fieldnames=fieldnames) as f:
                    f.write(data)

    @url(r'/api/lm/users/check')
    @authorize('lm:users:check')
    @endpoint(api=True)
    def handle_api_users_check(self, http_context):
        """
        Launch `sophomorix-check` to find out if more actions are required to
        save the changes to the sophomorix objects.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Output of `sophomorix-check`
        :rtype: dict
        """

        sophomorixCommand = ['sophomorix-check', '-jj']
        results = lmn_getSophomorixValue(sophomorixCommand, '')
        ## Remove UPDATE entries which are also in KILL ( necessary to show it in KILL and UPDATE ? )

        if "CHECK_RESULT" not in results:
            # TODO : Unknow error with sophomorix-check not specified in json
            return False

        if "UPDATE" in results["CHECK_RESULT"] and "KILL" in results["CHECK_RESULT"]:
            for user_update in tuple(results["CHECK_RESULT"]["UPDATE"]):
                if user_update in results["CHECK_RESULT"]["KILL"]:
                    del results["CHECK_RESULT"]["UPDATE"][user_update]
        return results

    @url(r'/api/lm/users/apply')
    @authorize('lm:users:apply')
    @endpoint(api=True)
    def handle_api_users_apply(self, http_context):
        """
        Performs an add, update or kill of sophomorix objects after a
        `sophomorix-check` if necessary.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        path = '/tmp/sophomorix.log'
        # TODO: Update this function for output
        # replace sophomorix-move by sophomorix-update
        open(path, 'w').close()

        script = ''
        if http_context.json_body()['doAdd']:
            script += f'sophomorix-add >> {path};'
        if http_context.json_body()['doMove']:
            script += f'sophomorix-update >> {path};'
        if http_context.json_body()['doKill']:
            script += f'sophomorix-kill >> {path};'

        try:
            subprocess.check_call(script, shell=True, env={'LC_ALL': 'C'})
        except Exception as e:
            raise EndpointError(None, message=str(e))

    @url(r'/api/lm/users/password')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_password(self, http_context):
        """
        Update users passwords through `sophomorix-passwd`.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Output of `sophomorix-passwd`
        :rtype: dict
        """

        action = http_context.json_body()['action']
        users = http_context.json_body()['users']
        user = ','.join([x.strip() for x in users])
        # Read Password
        if action == 'get':
            sophomorixCommand = ['sophomorix-user', '--info', '-jj', '-u', user]
            return lmn_getSophomorixValue(sophomorixCommand, '/USERS/'+user+'/sophomorixFirstPassword')
        if action == 'set-initial':
            sophomorixCommand = ['sophomorix-passwd', '--set-firstpassword', '-jj', '-u', user, '--use-smbpasswd']
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'set-random':
            # TODO: Password length should be read from school settings
            sophomorixCommand = ['sophomorix-passwd', '-u', user, '--random', '8', '-jj', '--use-smbpasswd']
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN')
        if action == 'set':
            password = http_context.json_body()['password']
            sophomorixCommand = ['sophomorix-passwd', '-u', user, '--pass', password, '-jj', '--use-smbpasswd']
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN', sensitive=True)
        if action == 'set-actual':
            password = http_context.json_body()['password']
            sophomorixCommand = ['sophomorix-passwd', '-u', user, '--pass', password, '--nofirstpassupdate', '--hide', '-jj', '--use-smbpasswd']
            return lmn_getSophomorixValue(sophomorixCommand, 'COMMENT_EN', sensitive=True)

    @url(r'/api/lm/users/change-school-admin')
    @authorize('lm:users:schooladmins:create')
    @endpoint(api=True)
    def handle_api_users_schooladmins_create(self, http_context):
        """
        Create or delete school admins.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string
        """
        school = self.context.schoolmgr.school
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
        """
        Create or delete global admins.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string
        """

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

    @url(r'/api/lm/users/get-classes')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_get_classes(self, http_context):
        """
        Get list of all classes.
        Method GET: get all classes lists for teachers.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: With GET, list of classes, one classe per dict
        :rtype: With GET, list of dict
        """

        school = self.context.schoolmgr.school
        if http_context.method == 'GET':

            sophomorixCommand = ['sophomorix-query', '--class', '--schoolbase', school, '--group-full', '-jj']

            with authorize('lm:users:students:read'):
                # Check if there are any classes if not return empty list
                classes_raw = lmn_getSophomorixValue(sophomorixCommand, 'GROUP')
                classes = []
                for c, details in classes_raw.items():
                    if details["sophomorixHidden"] == "FALSE":
                        classes.append(c)
                with authorize('lm:users:teachers:read'):
                    # append empty element. This references to all users
                    classes.append('')
                    # add also teachers passwords
                    if school == 'default-school':
                        classes.append('teachers')
                    else:
                        classes.append(school+'-teachers')
                return classes

    @url(r'/api/lm/users/print-individual')
    @authorize('lm:users:teachers:read') #TODO
    @endpoint(api=True)
    def handle_api_users_print_individual(self, http_context):
        """
        Print individual passwords for selected users as PDF, one per page.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        school = self.context.schoolmgr.school

        if http_context.method == 'POST':
            user = http_context.json_body()['user']
            user_list = http_context.json_body()['user_list']

            sophomorixCommand = [
                'sudo', 'sophomorix-print',
                '--school', school,
                '--caller', str(user),
                '--user', ','.join(user_list),
                '--one-per-page',
            ]

            # sophomorix-print needs the json parameter at the very end
            sophomorixCommand.extend(['-jj'])

            # generate real shell environment for sophomorix print
            shell_env = {'TERM': 'xterm', 'SHELL': '/bin/bash',  'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',  'HOME': '/root', '_': '/usr/bin/python3'}
            try:
                subprocess.check_call(sophomorixCommand, shell=False, env=shell_env)
            except subprocess.CalledProcessError as e:
                return 'Error '+str(e)
            return 'success'

    @url(r'/api/lm/users/print')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_print(self, http_context):
        """
        Print passwords as PDF
        Method POST: all passwords.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        school = self.context.schoolmgr.school
        config_template = self.context.schoolmgr.custom_fields.get(
            'passwordTemplates', {'multiple': '', 'individual': ''}
        )
        config_template_individual = config_template.get('individual', '')
        config_template_multiple = config_template.get('multiple', '')

        if http_context.method == 'POST':
            user = http_context.json_body()['user']
            one_per_page = http_context.json_body()['one_per_page']
            pdflatex = http_context.json_body()['pdflatex']
            schoolclass = http_context.json_body()['schoolclass']
            template = ''
            sophomorixCommand = ['sudo', 'sophomorix-print', '--school', school, '--caller', str(user)]
            if one_per_page:
                try:
                    template = http_context.json_body()['template_one_per_page']['path']
                except TypeError:
                    template = config_template_individual
                    if not template:
                        sophomorixCommand.extend(['--one-per-page'])
            else:
                try:
                    template = http_context.json_body()['template_multiple']['path']
                except TypeError:
                    template = config_template_multiple
            if template:
                sophomorixCommand.extend(['--template', template])
            if pdflatex:
                sophomorixCommand.extend(['--command'])
                sophomorixCommand.extend(['pdflatex'])
            if schoolclass:
                sophomorixCommand.extend(['--class', ','.join(schoolclass)])
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
            shell_env = {'TERM': 'xterm', 'SHELL': '/bin/bash',  'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',  'HOME': '/root', '_': '/usr/bin/python3'}
            try:
                subprocess.check_call(sophomorixCommand, shell=False, env=shell_env)


            except subprocess.CalledProcessError as e:
                return 'Error '+str(e)
            return 'success'
            # return lmn_getSophomorixValue(sophomorixCommand, 'JSONINFO')

    @url(r'/api/lm/users/print-download/(?P<name>.+)')
    @authorize('lm:users:passwords')
    @endpoint(api=False, page=True)
    def handle_api_users_print_download(self, http_context, name):
        """
        Changes header to deliver a downloadable PDF.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param name: Name of the file
        :type name: string
        """

        root = '/var/lib/sophomorix/print-data/'
        path = os.path.abspath(os.path.join(root, name))

        if not path.startswith(root):
            return http_context.respond_forbidden()
        return http_context.file(path, inline=False, name=name.encode())

    @url(r'/api/lm/users/test-first-password/(?P<name>.+)')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_api_users_test_password(self, http_context, name):
        """
        Check if first password is still set.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param name: User's uid
        :type name: string
        :return: First password still set or not
        :rtype: bool
        """

        line = subprocess.check_output(['sudo', 'sophomorix-passwd', '--test-firstpassword', '-u', name]).splitlines()[-4]
        return b'1 OK' in line

    @url(r'/api/lm/users/get-group-quota')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_group_quota(self, http_context):
        """
        Get samba share limits for a group list. Prepare type key for style
        (danger, warning, success) to display status.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            groupList = http_context.json_body()['groupList']
            sophomorixCommand = ['sophomorix-quota', '--smbcquotas-only', '-i', '--user', ','.join(groupList), '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'QUOTA/USERS')

            quotaMap = {}
            school = self.context.schoolmgr.school
            # Only read default-school for the moment, must be maybe adapted later
            for user in groupList:
                share = result[user]["SHARES"][school]['smbcquotas']
                if int(share['HARDLIMIT_MiB']) == share['HARDLIMIT_MiB']:
                    # Avoid strings for non set quotas
                    used = int(float(share['USED_MiB']) / share['HARDLIMIT_MiB'] * 100)
                    soft = int(float(share['SOFTLIMIT_MiB']) / share['HARDLIMIT_MiB'] * 100)
                    if used >= 80:
                        state = "danger"
                    elif used >= 60:
                        state = "warning"
                    else:
                        state = "success"

                    quotaMap[user] = {
                        "USED": used,
                        "SOFTLIMIT": soft,
                        "TYPE": state,
                    }
                else:
                    quotaMap[user] = {
                        "USED": 0,
                        "SOFTLIMIT": 0,
                        "TYPE": "success",
                    }
            return quotaMap

    @url(r'/api/lm/custom')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom(self, http_context):
        """
        Update a custom sophomorix field.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            n = http_context.json_body()['index']
            user = http_context.json_body()['user']
            value = http_context.json_body()['value']

            try:
                command = ['sophomorix-user', '-u', user, f'--custom{n}', value, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

    @url(r'/api/lm/custommulti/add')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom_mutli_add(self, http_context):
        """
        Add a sophomorix field in custom multi.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            n = http_context.json_body()['index']
            user = http_context.json_body()['user']
            value = http_context.json_body()['value']

            try:
                command = ['sophomorix-user', '-u', user, f'--add-custom-multi{n}', value, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

    @url(r'/api/lm/custommulti/remove')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom_multi_remove(self, http_context):
        """
        Remove a sophomorix field in custom multi.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            n = http_context.json_body()['index']
            user = http_context.json_body()['user']
            value = http_context.json_body()['value']

            try:
                command = ['sophomorix-user', '-u', user, f'--remove-custom-multi{n}', value, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

    @url(r'/api/lm/setProxyAddresses')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_set_proxy_addresses(self, http_context):
        """
        Set proxyAddresses, e.g. emails, for an user.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            user = http_context.json_body()['user']
            addresses = ','.join(http_context.json_body()['addresses'])

            try:
                command = ['sophomorix-user', '-u', user, '--set-proxy-addresses', addresses, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

    @url(r'/api/lm/changeProxyAddresses')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_set_proxy_addresses(self, http_context):
        """
        Add or remove an email in proxyAddresses, e.g. emails, for an user.
        Method POST.
        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            action = http_context.json_body()['action']

            if action not in ['add', 'remove']:
                raise EndpointError(None)

            user = http_context.json_body()['user']
            address = http_context.json_body()['address']

            try:
                command = ['sophomorix-user', '-u', user, f'--{action}-proxy-addresses', address, '-jj']
                result = lmn_getSophomorixValue(command, '')
            except IndexError:
                # No error output from sophomorix yet
                raise EndpointError(None)

    @url(r'/api/lm/filterCustomCSV')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_custom_csv(self, http_context):
        """
        Run sophomorix-newfile in order to apply a custom script for a newly custom csv file.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if http_context.method == 'POST':
            # E.g. /tmp/students.csv
            tmp_path = http_context.json_body()['tmp_path']
            # E.g. students.csv
            target = http_context.json_body()['userlist']

            command = ['sophomorix-newfile', tmp_path, '--name', target, '-jj']
            result = lmn_getSophomorixValue(command, 'OUTPUT/0')

            if result['TYPE'] == "ERROR":
                    return ["ERROR", result['MESSAGE_EN']]
            if result['TYPE'] == "LOG":
                    return ["LOG", result['LOG']]

    @url(r'/api/lm/users/binduser/(?P<level>.*)')
    @authorize('lm:users:globaladmins:create')
    @endpoint(api=True)
    def handle_api_users_binduser(self, http_context, level=''):
        """
        List or create school and global bindusers.
        Method POST and GET

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param level: school or global
        :type level: basestring
        :return: State of the command
        :rtype: string or list
        """

        secret_path = '/etc/linuxmuster/.secret/'

        if http_context.method == 'GET':
            binduser_list = []
            sophomorixCommand = ['sophomorix-query', f'--{level}binduser', '--user-full', '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, '')
            if 'USER' in result.keys():
                for username, details in result['USER'].items():
                    if details['sophomorixRole'] == f"{level}binduser":
                        details['pw'] = False
                        if os.path.isfile(os.path.join(secret_path, username)):
                            details['pw'] = True
                        binduser_list.append(details)
                return binduser_list
            return []

        if http_context.method == 'POST':
            binduser = http_context.json_body()['binduser']
            # level may be global or school
            level = http_context.json_body()['level']
            school_option = ''
            if level == 'school':
                school_option = ('--school', self.context.schoolmgr.school)
            sophomorixCommand = ['sophomorix-admin',
                                 f'--create-{level}-binduser', binduser,
                                 *school_option,
                                 '--random-passwd-save', '-jj'
                                 ]
            result = lmn_getSophomorixValue(sophomorixCommand, '')
            return result['COMMENT_EN']

    @url(r'/api/lm/users/showBindPW')
    @authorize('lm:users:globaladmins:create')
    @endpoint(api=True)
    def handle_api_users_showpw_binduser(self, http_context):
        """
        Get the bind user's password.
        Method POST

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: State of the command
        :rtype: string or list
        """

        if os.getuid() != 0:
            return EndpointReturn(403)

        if http_context.method == 'POST':
            user = http_context.json_body()['user']
            secret_path = os.path.join('/etc/linuxmuster/.secret/', user)

            if os.path.isfile(secret_path):
                with open(secret_path, 'r') as f:
                    return f.read()