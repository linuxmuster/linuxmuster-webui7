try:
    from .main import ItemProvider
except ImportError:
    # ItemProvider only accessible in dev mode
    pass
from .views import Handler
