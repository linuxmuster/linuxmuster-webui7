"""
Module to handle an user crontab file.
"""

from jadi import component

from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize, AuthenticationService
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.lmn_crontab.manager import CronManager
from reconfigure.items.crontab import CrontabNormalTaskData, CrontabSpecialTaskData, CrontabEnvSettingData

HOLIDAY_PREFIX_TEST = '/usr/sbin/linuxmuster-holiday '

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/crontab')
    @authorize('lm:crontab:read')
    @endpoint(api=True)
    def handle_api_get_crontab(self, http_context):
        """
        Get the cron content through ConManager and store it in a dict.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Cron jobs
        :rtype: dict
        """

        def _parse_crontab_dict(crontab_dict):
            for job in crontab_dict['normal_tasks']:
                job['school'] = 'default-school'
                if job['command'].startswith(HOLIDAY_PREFIX_TEST):
                    job['disable_holiday'] = True
                    holiday_command, job['command'] = job['command'].split('&&')
                    # School option used, we can extract the school
                    if '-s' in holiday_command:
                        job['school'] = holiday_command.strip().split()[-1]
                else:
                    job['disable_holiday'] = False

            for job in crontab_dict['special_tasks']:
                job['school'] = 'default-school'
                if job['command'].startswith(HOLIDAY_PREFIX_TEST):
                    job['disable_holiday'] = True
                    holiday_command, job['command'] = job['command'].split('&&')
                    # School option used, we can extract the school
                    if '-s' in holiday_command:
                        job['school'] = holiday_command.strip().split()[-1]
                else:
                    job['disable_holiday'] = False

            return crontab_dict

        school = self.context.schoolmgr.school

        user = self.context.identity
        profil = AuthenticationService.get(self.context).get_provider().get_profile(user)

        if profil['sophomorixRole'] == 'globaladministrator':
            # Load global-admin and root crontabs for all global admins
            crontab = CronManager.get(self.context).load_tab('global-admin')
            crontab_dict = crontab.tree.to_dict()

            crontabRoot = CronManager.get(self.context).load_tab('root')
            crontab_root_dict = crontabRoot.tree.to_dict()

            return _parse_crontab_dict(crontab_dict), _parse_crontab_dict(crontab_root_dict), school

    @post(r'/api/lmn/crontab')
    @authorize('lm:crontab:write')
    @endpoint(api=True)
    def handle_api_save_crontab(self, http_context):
        """
        Store cron data from frontend in a cron file through CronManager.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: True if successfull
        :rtype: bool
        """

        def setTask(obj, values):
            """
            Utility to convert angular values in Python Crontab objects.
            :param obj: Crontab object
            :type obj: object
            :param values: Crontab values as dict
            :type values: dict
            :return: Crontab object
            :rtype: object
            """

            if 'disable_holiday' in values:
                school = self.context.schoolmgr.school
                if values['disable_holiday']:
                    school = values.get('school', school)
                    values['command'] = f'{HOLIDAY_PREFIX_TEST} -s {school} && {values["command"]}'
                del values['disable_holiday']
                del values['school']

            for k,v in values.items():
                setattr(obj, k, v)
            return obj

        def fill_crontab(crontab, data):
            for _type, values_list in data.items():
                for values in values_list:
                    if _type == 'normal_tasks':
                        crontab.tree.normal_tasks.append(setTask(CrontabNormalTaskData(), values))
                    elif _type == 'special_tasks':
                        crontab.tree.special_tasks.append(setTask(CrontabSpecialTaskData(), values))
                    elif _type == 'env_settings':
                        crontab.tree.env_settings.append(setTask(CrontabEnvSettingData(), values))
            return crontab

        # Create empty config
        user = self.context.identity
        crontabs =  http_context.json_body()

        crontabGA = CronManager.get(self.context).load_tab(None)
        crontabGA = fill_crontab(crontabGA, crontabs['globaladministrator'])

        crontabRoot = CronManager.get(self.context).load_tab(None)
        crontabRoot = fill_crontab(crontabRoot, crontabs['root'])

        profil = AuthenticationService.get(self.context).get_provider().get_profile(user)

        try:
            if profil['sophomorixRole'] == 'globaladministrator':
                CronManager.get(self.context).save_tab('global-admin', crontabGA)
                CronManager.get(self.context).save_tab('root', crontabRoot)
                return True
            return False
        except Exception as e:
            raise EndpointError(e)
