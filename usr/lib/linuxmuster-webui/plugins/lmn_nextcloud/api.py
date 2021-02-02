import yaml
import os

class ConfigLoader():
    def __init__(self, path):
        self.data = None
        self.path = os.path.abspath(path)

    def __str__(self):
        return self.path

    def load(self):
        if os.path.exists(self.path) == False:
            return { "status": "error", "message": "Configfile not found!" }
        else:
            return { "status": "success", "data": yaml.load(open(self.path)) }

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True))

def loadSettings():
    settings = ConfigLoader('/etc/linuxmuster/webui/nextcloud/nextcloud_config.json')
    return settings.load()