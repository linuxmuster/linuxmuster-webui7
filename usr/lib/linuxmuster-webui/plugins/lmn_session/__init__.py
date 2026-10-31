import os
import logging

if os.path.isfile('/etc/linuxmuster/webui/disable_new_session_plugin'):
    try:
        with open('/etc/linuxmuster/webui/disable_new_session_plugin') as tag_file:
            tag = tag_file.read()[0]
        if tag == '1':
            logging.info("Disabling new session plugin")
        else:
            logging.warning("/etc/linuxmuster/webui/disable_new_session_plugin does not contain a valid tag (should be 1)")
            logging.info('New session is enabled')
            from .main import *
            from .views import *
    except IndexError as e:
        logging.warning("/etc/linuxmuster/webui/disable_new_session_plugin does not contain a valid tag (is empty)")
        logging.info('New session is enabled')
        from .main import *
        from .views import *
else:
    from .main import *
    from .views import *
