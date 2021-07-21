"""
Manage per user or group quota configuration.
"""

import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_common.api import lmn_getSophomorixValue
from aj.plugins.lmn_common.lmnfile import LMNFile
from configparser import ConfigParser

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lm/quotas')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_quotas(self, http_context):
        """
        Get all quotas informations from `school.conf` and LDAP tree.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All quotas informations
        :rtype: list of dict
        """

        school = 'default-school'
        settings_path = '/etc/linuxmuster/sophomorix/'+school+'/school.conf'

        quota_types = {
            'QUOTA_DEFAULT_GLOBAL':'linuxmuster-global',
            'QUOTA_DEFAULT_SCHOOL':'default-school',
        }

        if http_context.method == 'GET':
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

    @url(r'/api/lm/quotas/group')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_class_quotas(self, http_context):
        """
        Get quotas for projects and classes.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Dict with all quotas informations
        :rtype: dict
        """

        if http_context.method == 'GET':
            groups = {'adminclass':{}, 'project':{}}
            shares = ['linuxmuster-global', 'default-school']

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

    @url(r'/api/lm/quotas/save')
    @authorize('lm:quotas:configure')
    @endpoint(api=True)
    def handle_api_save_quotas(self, http_context):
        """
        Register the new quota values through sophomorix.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        quota_types = {
            'QUOTA_DEFAULT_GLOBAL':'linuxmuster-global',
            'QUOTA_DEFAULT_SCHOOL':'default-school',
        }

        if http_context.method == 'POST':
            ## Update quota per user, but not applied yet
            ## Not possible to factorise the command for many users
            for _, userDict in http_context.json_body()['users'].items():
                for _,values in userDict.items():
                    if values['quota'] == 'MAILQUOTA_DEFAULT':
                        sophomorixCommand = ['sophomorix-user', '--mailquota', '%s' % (values['value']), '-u', values['login'], '-jj']
                    else:
                        sophomorixCommand = ['sophomorix-user', '--quota', '%s:%s:---' % (quota_types[values['quota']], values['value']), '-u', values['login'], '-jj']
                    lmn_getSophomorixValue(sophomorixCommand, '')

            ## Update quota per class, but not applied yet
            for _, grpDict in http_context.json_body()['groups']['adminclass'].items():
                if grpDict['quota'] == 'mailquota':
                    sophomorixCommand = ['sophomorix-class', '-c', grpDict['group'], '--mailquota', '%s:' % grpDict['value'], '-jj']
                else:
                    sophomorixCommand = ['sophomorix-class', '-c', grpDict['group'], '--quota', '%s:%s:---' % (grpDict['quota'], grpDict['value']), '-jj']
                lmn_getSophomorixValue(sophomorixCommand, '')

            ## Update quota per project, but not applied yet
            for _, grpDict in http_context.json_body()['groups']['project'].items():
                if grpDict['quota'] == 'mailquota':
                    sophomorixCommand = ['sophomorix-project', '-p', grpDict['group'], '--addmailquota', '%s:' % grpDict['value'], '-jj']
                else:
                    sophomorixCommand = ['sophomorix-project', '-p', grpDict['group'], '--addquota', '%s:%s:---' % (grpDict['quota'], grpDict['value']), '-jj']
                lmn_getSophomorixValue(sophomorixCommand, '')

    @url(r'/api/lm/ldap-search')
    @authorize('lm:quotas:configure')
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

        if http_context.method == 'POST':

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

    @url(r'/api/lm/quotas/apply')
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
