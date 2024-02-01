"""
Manage per user or group quota configuration.
"""

import os
import pwd
import subprocess

from jadi import component
from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.api import lmn_getSophomorixValue, samba_workgroup
from aj.plugins.lmn_common.lmnfile import LMNFile
from linuxmusterTools.quotas import list_user_files


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/quota/user/(?P<user>.+)')
    @endpoint(api=True)
    def handle_api_quota(self, http_context, user):
        """
        Get quota informations from user through sophomorix-query.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param user: User login
        :type user: string
        :return: All quotas informations from user
        :rtype: dict
        """

        if user != self.context.identity and os.getuid() != 0:
            http_context.respond_forbidden()
            return {}

        if user != 'root':
            sophomorixCommand = ['sophomorix-query', '--sam', user, '--user-full', '--quota-usage', '-jj']
            jsonpath = 'USER/' + user
            data = lmn_getSophomorixValue(sophomorixCommand, jsonpath)
            return {
                'QUOTA_USAGE_BY_SHARE': data['QUOTA_USAGE_BY_SHARE'],
                'sophomorixCloudQuotaCalculated': data['sophomorixCloudQuotaCalculated'],
                'sophomorixMailQuotaCalculated': data['sophomorixMailQuotaCalculated'],
            }
        return {}

    @get(r'/api/lmn/quota/usermap/(?P<user>[a-z0-9\-_]*)')
    @authorize('lm:users:passwords')
    @endpoint(api=True)
    def handle_group_quota(self, http_context, user=None):
        """
        Get samba share limits for a group list. Prepare type key for style
        (danger, warning, success) to display status.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas for specified users
        :rtype: dict
        """

        if user is None:
            return ''

        school = self.context.schoolmgr.school

        sophomorixCommand = ['sophomorix-quota', '--smbcquotas-only', '-i', '--user', user, '-jj']
        json_path = f'QUOTA/USERS/{user}/SHARES/{school}/smbcquotas'
        share = lmn_getSophomorixValue(sophomorixCommand, json_path)

        quotaMap = {}

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

    @get(r'/api/lmn/quota/quotas')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_quotas(self, http_context):
        """
        Get all quotas informations from `school.conf` and LDAP tree.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas informations
        :rtype: list of dict
        """

        school = self.context.schoolmgr.school
        settings_path = f'{self.context.schoolmgr.configpath}school.conf'

        quota_types = {
            'QUOTA_DEFAULT_GLOBAL':'linuxmuster-global',
            'QUOTA_DEFAULT_SCHOOL':school,
        }

        ## Parse csv config file
        with LMNFile(settings_path, 'r') as set:
            settings = set.data

        ## Get list of non default quota user, others get the default value
        ## Teachers and students are mixed in the same dict
        non_default = {'teacher':{'list':[]}, 'student':{'list':[]}, 'schooladministrator':{'list':[]}}

        sophomorixCommand = ['sophomorix-quota', '-i', '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, 'NONDEFAULT_QUOTA/' + school + '/USER')
        for login, values in result.items():
            role = values['sophomorixRole']
            non_default[role][login] = values
            non_default[role]['list'].append({'sn':values['sn'], 'login':login, 'givenname':values['givenName']})

            # Normal shares
            if 'QUOTA' in values.keys():
                for tag, share in quota_types.items():
                    if share not in values['QUOTA'] or values['QUOTA'][share]['VALUE'] == "---":
                        values['QUOTA'][tag] = settings['role.'+role][tag]
                    else:
                        values['QUOTA'][tag] = int(values['QUOTA'][share]['VALUE'])
                        del values['QUOTA'][share]
            else:
                values['QUOTA'] = {}
                for tag, _ in quota_types.items():
                    values['QUOTA'][tag] = settings['role.'+role][tag]

            # Mailquota
            if 'MAILQUOTA' in values.keys():
                values['QUOTA']['MAILQUOTA_DEFAULT'] = int(values['MAILQUOTA']['VALUE'])
            else:
                values['QUOTA']['MAILQUOTA_DEFAULT'] = settings['role.'+role]['MAILQUOTA_DEFAULT']

            # Cloudquota
            values['QUOTA']['CLOUDQUOTA_PERCENTAGE'] = settings['role.'+role]['CLOUDQUOTA_PERCENTAGE']

        return [non_default, settings]

    @get(r'/api/lmn/quota/groups')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_class_quotas(self, http_context):
        """
        Get quotas for projects and classes.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Dict with all quotas informations
        :rtype: dict
        """
        school = self.context.schoolmgr.school

        groups = {'adminclass':{}, 'project':{}}
        shares = ['linuxmuster-global', school]

        sophomorixCommand = ['sophomorix-class', '-i', '-jj']
        result = lmn_getSophomorixValue(sophomorixCommand, 'GROUPS')

        for group, details in result.items():
            if 'sophomorixType' in details.keys():
                ## Class
                if details['sophomorixType'] == 'adminclass':
                    details['QUOTA'] = {}
                    details['QUOTA']['mailquota'] = {'value':0 if details['sophomorixMailQuota'].startswith('---') else int(details['sophomorixMailQuota'].split(':')[0])}
                    for line in details['sophomorixQuota']:
                        share,value,comment,_ = line.split(':')
                        details['QUOTA'][share] = {'value':int(value) if value != '---' else 0, 'comment':comment}
                    for share in shares:
                        if share not in details['QUOTA'].keys():
                            details['QUOTA'][share] = {'value':0, 'comment':''}

                    groups[details['sophomorixType']][group] = details

                ## Project
                elif details['sophomorixType'] == 'project':
                    details['QUOTA'] = {}
                    details['QUOTA']['mailquota'] = {'value':0 if details['sophomorixAddMailQuota'].startswith('---') else int(details['sophomorixAddMailQuota'].split(':')[0])}
                    for line in details['sophomorixAddQuota']:
                        share,value,comment,_ = line.split(':')
                        details['QUOTA'][share] = {'value':int(value) if value != '---' else 0, 'Comment':comment}
                    for share in shares:
                        if share not in details['QUOTA'].keys():
                            details['QUOTA'][share] = {'value':0, 'Comment':''}
                    groups[details['sophomorixType']][group] = details
        return groups

    @post(r'/api/lmn/quota/save')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_save_quotas(self, http_context):
        """
        Register the new quota values through sophomorix.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """
        school = self.context.schoolmgr.school

        quota_types = {
            'QUOTA_DEFAULT_GLOBAL':'linuxmuster-global',
            'QUOTA_DEFAULT_SCHOOL':school,
        }

        ## Update quota per user, but not applied yet
        ## Not possible to factorise the command for many users
        for _, userDict in http_context.json_body()['users'].items():
            for _,values in userDict.items():
                if values['quota'] == 'MAILQUOTA_DEFAULT':
                    sophomorixCommand = ['sophomorix-user', '--mailquota', f"{values['value']}", '-u', values['login'], '-jj']
                else:
                    sophomorixCommand = ['sophomorix-user', '--quota', f"{quota_types[values['quota']]}:{values['value']}:---", '-u', values['login'], '-jj']
                lmn_getSophomorixValue(sophomorixCommand, '')

        ## Update quota per class, but not applied yet
        for _, grpDict in http_context.json_body()['groups']['adminclass'].items():
            if grpDict['quota'] == 'mailquota':
                sophomorixCommand = ['sophomorix-class', '-c', grpDict['group'], '--mailquota', f"{grpDict['value']}:", '-jj']
            else:
                sophomorixCommand = ['sophomorix-class', '-c', grpDict['group'], '--quota', f"{grpDict['quota']}:{grpDict['value']}:---", '-jj']
            lmn_getSophomorixValue(sophomorixCommand, '')

        ## Update quota per project, but not applied yet
        for _, grpDict in http_context.json_body()['groups']['project'].items():
            if grpDict['quota'] == 'mailquota':
                sophomorixCommand = ['sophomorix-project', '-p', grpDict['group'], '--addmailquota', f"{grpDict['value']}:", '-jj']
            else:
                sophomorixCommand = ['sophomorix-project', '-p', grpDict['group'], '--addquota', f"{grpDict['quota']}:{grpDict['value']}:---", '-jj']
            lmn_getSophomorixValue(sophomorixCommand, '')

    @post(r'/api/lmn/ldap-search')
    @authorize('lm:quotas:ldap-search')
    @endpoint(api=True)
    def handle_api_ldap_search(self, http_context):
        """
        Query usernames for filter in frontend.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: list of usernames with details, one user per dict
        :rtype: list of dict
        """

        # TODO : url already exists in groupmembership, must be factorized ?

        # Problem with unicode In&egraves --> In\xe8s (py) --> In\ufffds (replace)
        # Should be In&egraves --> Ines ( sophomorix supports this )
        # login = http_context.json_body()['login'].decode('utf-8', 'replace')

        login = http_context.json_body()['login']
        role = http_context.json_body()['role']

        ## --teacher limit the query only to teachers
        if role:
            role = '--' + role

        resultArray = []

        try:
            sophomorixCommand = ['sophomorix-query', '--anyname', login+'*', role, '-jj']
            result = lmn_getSophomorixValue(sophomorixCommand, 'USER')

            for user, details in result.items():
                resultArray.append({
                        'label':details['sn'] + " " + details['givenName'] + " (" + user + ")",
                        'login':details['sAMAccountName'],
                        'role':details['sophomorixRole'],
                        'displayName':details['sn'] + " " + details['givenName']
                        })
        except:
            # Ignore SophomorixValue errors
            pass
        return resultArray

    @post(r'/api/lmn/quota/apply')
    @authorize('lm:quotas:apply')
    @endpoint(api=True)
    def handle_api_apply(self, http_context):
        """
        Apply new quota configuration.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        try:
            subprocess.check_call('sophomorix-quota > /tmp/apply-sophomorix.log', shell=True)
        except Exception as e:
            raise EndpointError(None, message=str(e))

    @get(r'/api/lmn/quota/check/(?P<user>[a-z0-9\-_]*)')
    @authorize('lm:quotas:apply')
    @endpoint(api=True)
    def handle_api_check_quota(self, http_context, user=''):
        """
        Lists main directories used quota for a given user.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param user: user login
        :type user: basestring
        :return: directories containing user's files and the total size used
        :rtype: dict
        """

        # if isAdmin or user == self.context.identity

        return list_user_files(user)

