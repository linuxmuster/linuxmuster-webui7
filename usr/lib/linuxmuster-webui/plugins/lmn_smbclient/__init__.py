# pyflakes: disable-all
import logging
import smbprotocol
import spnego

from .main import *
from .views.lmnsmbclient import *
from .views.lmnwebdav import *

# Disable DEBUG/INFO level because of incompatibility with ajenti logger
logging.getLogger('smbprotocol').setLevel(logging.WARNING)
logging.getLogger('smbprotocol.connection').setLevel(logging.WARNING)
logging.getLogger('smbprotocol.negotiate').setLevel(logging.WARNING)
logging.getLogger('smbprotocol.tree').setLevel(logging.WARNING)
logging.getLogger('smbprotocol.open').setLevel(logging.WARNING)
logging.getLogger('spnego.gss').setLevel(logging.WARNING)
logging.getLogger('spnego.negotiate').setLevel(logging.WARNING)
logging.getLogger('smbprotocol.transport').setLevel(logging.WARNING)
logging.getLogger('smbprotocol.session').setLevel(logging.WARNING)
