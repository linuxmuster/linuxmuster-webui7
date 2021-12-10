import os
import logging
import subprocess

from aj.plugins.core.api.tasks import Task
from aj.auth import authorize


class Cloop2Qcow2(Task):
    name = _('Convert to qcow2')

    def __init__(self, context, items=None):
        Task.__init__(self, context)
        self.items = items

    @authorize('lm:linbo:configs')
    def run(self):
        logging.info(f'Converting {len(self.items)} items')

        for idx, item in enumerate(self.items):
            self.report_progress(message=item, done=idx, total=len(self.items))
            logging.info(f'Converting {item}')
            r = subprocess.call([
                '/usr/sbin/linbo-cloop2qcow2', os.path.join('/srv/linbo/', item)
            ])
            if r != 0:
                logging.warning(f'Conversion exited with code {r}')

        self.push('lmn_linbo', 'refresh')


