import os
import logging

if os.path.isfile('/etc/linuxmuster/webui/enable_old_session_plugin'):
    try:
        with open('/etc/linuxmuster/webui/enable_old_session_plugin') as tag_file:
            tag = tag_file.read()[0]
        if tag == '1':
            from .main import *
            from .views import *
            logging.info("Enabling old session plugin")
        else:
            logging.info("/etc/linuxmuster/webui/enable_old_session_plugin does not contain a valid tag (should be 1)")
            logging.info("Old session plugin stays disabled")
    except IndexError as e:
        logging.warning("/etc/linuxmuster/webui/enable_old_session_plugin does not contain a valid tag (is empty)")
        logging.info("Old session plugin stays disabled")
else:
    logging.info("Old session plugin stays disabled")
