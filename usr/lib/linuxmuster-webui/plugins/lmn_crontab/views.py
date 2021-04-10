"""
Module to handle an user crontab file.
"""

from jadi import component

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from .manager import CronManager
from reconfigure.items.crontab import CrontabNormalTaskData, CrontabSpecialTaskData, CrontabEnvSettingData

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/get_crontab')
    # @authorize('crontab:show')
    @endpoint(api=True)
    def handle_api_get_crontab(self, http_context):
        """
        Get the cron content through ConManager and store it in a dict.
        Method GET.
        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Cron jobs
        :rtype: dict
        """

        if http_context.method == 'GET':
            prepend_holiday = 'TestHolidays && '
            user = self.context.identity
            crontab = CronManager.get(self.context).load_tab(user)
            crontab_dict = crontab.tree.to_dict()
            for job in crontab_dict['normal_tasks']:
                if job['command'].startswith(prepend_holiday):
                    job['disable_holiday'] = True
                    job['command'] = job['command'][len(prepend_holiday):]
                else:
                    job['disable_holiday'] = False
            for job in crontab_dict['special_tasks']:
                if job['command'].startswith(prepend_holiday):
                    job['disable_holiday'] = True
                    job['command'] = job['command'][len(prepend_holiday):]
                else:
                    job['disable_holiday'] = False
            return crontab_dict

    @url(r'/api/save_crontab')
    # @authorize('crontab:show')
    @endpoint(api=True)
    def handle_api_save_crontab(self, http_context):
        """
        Store cron data from frontend in a cron file through CronManager.
        Method POST.
        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: True if successfull
        :rtype: bool
        """
        if http_context.method == 'POST':
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
                    if values['disable_holiday']:
                        values['command'] = 'TestHolidays && ' + values['command']
                    del values['disable_holiday']

                for k,v in values.items():
                    setattr(obj, k, v)
                return obj

            # Create empty config
            user = self.context.identity
            crontab = CronManager.get(self.context).load_tab(None)
            new_crontab = http_context.json_body()['crontab']
            for _type, values_list in new_crontab.items():
                for values in values_list:
                    if _type == 'normal_tasks':
                        crontab.tree.normal_tasks.append(setTask(CrontabNormalTaskData(), values))
                    elif _type == 'special_tasks':
                        crontab.tree.special_tasks.append(setTask(CrontabSpecialTaskData(), values))
                    elif _type == 'env_settings':
                        crontab.tree.env_settings.append(setTask(CrontabEnvSettingData(), values))
            try:
                CronManager.get(self.context).save_tab(user, crontab)
                return True
            except Exception as e:
                raise EndpointError(e)
