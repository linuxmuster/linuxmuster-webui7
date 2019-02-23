import datetime
now = datetime.datetime.now()
from jadi import component

from aj.plugins.dashboard.api import Widget


@component(Widget)
class RandomWidget(Widget):
    id = 'datetime'

    # display name
    name = 'Date Time'

    # template of the widget
    template = '/lmn_w_datetime:resources/partial/widget.html'

    # template of the configuration dialog
    config_template = '/lmn_w_datetime:resources/partial/widget.config.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        if 'format' not in config:
            return 'Not configured'
        return now.strftime(config['format'])
