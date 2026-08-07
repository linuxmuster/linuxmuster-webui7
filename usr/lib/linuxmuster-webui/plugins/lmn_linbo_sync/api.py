# -*- coding:utf8 -*-

from linuxmusterTools.linbo import LinboRemote, LinboRemoteParameterError


def build_linbo_remote(cmd_parameters):
    """
    Map the webui's cmd_parameters payload (built by the frontend) to a LinboRemote.

    :param cmd_parameters: All parameters to call linbo-remote
    :type cmd_parameters: dict
    :return: A LinboRemote ready to run()
    :rtype: LinboRemote
    """

    actions = ''
    if cmd_parameters['partition']:
        actions = 'partition,format'

    for action in ('format', 'sync', 'start'):
        for position in cmd_parameters['actions'][action]:
            actions = f'{actions},{action}:{position}' if actions else f'{action}:{position}'

    if cmd_parameters['acpi'] in ('halt', 'reboot'):
        actions = f'{actions},{cmd_parameters["acpi"]}' if actions else cmd_parameters['acpi']

    school = cmd_parameters['school']
    kwargs = {
        'cmd': actions,
        'onboot': cmd_parameters['prestart'],
        'disable_gui': cmd_parameters['disable_gui'],
        'broadcast': cmd_parameters['broadcast'],
        'school': None if school == 'default-school' else school,
    }

    if cmd_parameters['timeout'] > 0:
        kwargs['wol'] = int(cmd_parameters['timeout'])
        if cmd_parameters['bypass']:
            kwargs['bypass'] = True

    target = cmd_parameters['target']
    if target['type'] == 'group':
        kwargs['group'] = target['host']
    else:
        kwargs['clients'] = [target['host']]

    return LinboRemote(**kwargs)


def run(cmd_parameters):
    """
    Build and run a linbo-remote command from the webui's cmd_parameters payload.

    :param cmd_parameters: All parameters to call linbo-remote
    :type cmd_parameters: dict
    :return: {'status': 0, 'msg': <output>} on success, {'status': 1, 'msg': <error>} otherwise
    :rtype: dict
    """

    remote = build_linbo_remote(cmd_parameters)
    try:
        return remote.run()
    except LinboRemoteParameterError as e:
        return {'status': 1, 'msg': str(e)}
