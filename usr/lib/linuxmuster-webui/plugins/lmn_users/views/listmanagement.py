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
from aj.api.http import get, post, url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.api import lmn_getSophomorixValue
from aj.plugins.lmn_common.lmnfile import LMNFile


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context


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

        if "CHECK_RESULT" in results:
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
            try:
                result = lmn_getSophomorixValue(command, 'OUTPUT/0')

                if result['TYPE'] == "ERROR":
                        return ["ERROR", result['MESSAGE_EN']]
                if result['TYPE'] == "LOG":
                        return ["LOG", result['LOG']]
            except UnicodeDecodeError:
                return ["ERROR", "sophomorix was not able to detect the encoding of the file."]

