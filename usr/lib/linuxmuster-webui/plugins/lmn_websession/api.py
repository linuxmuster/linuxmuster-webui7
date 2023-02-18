import requests
import hashlib
import json
import xmltodict
import yaml
import os

class ConfigLoader():
    def __init__(self, path):
        self.data = None
        self.path = os.path.abspath(path)

    def __str__(self):
        return self.path

    def load(self):
        if not os.path.exists(self.path):
            return { "status": "error", "message": "Configfile not found!" }
        else:
            return { "status": "success", "data": yaml.load(open(self.path), Loader=yaml.SafeLoader) }

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True))

def replaceSpecialChars(string):
    string = string.replace(u'ü', 'ue')
    string = string.replace(u'ö', 'oe')
    string = string.replace(u'ä', 'ae')
    string = string.replace(u'Ü', 'Ue')
    string = string.replace(u'Ö', 'Oe')
    string = string.replace(u'Ä', 'Ae')
    string = string.replace(u'ß', 'ss')
    return string

def loadSettings():
    settings = ConfigLoader('/etc/linuxmuster/webui/websession/websession_config.json')
    return settings.load()

def loadList():
    sessionList = ConfigLoader('/etc/linuxmuster/webui/websession/websession_list.json')
    return sessionList.load()

def bbbApiCall(action):
    settings = loadSettings()["data"]
    bbb_instance = settings['settings']['bbbInstance']
    checksum = bbbGenerateChecksum(action)
    session = requests.Session()
    result_xml = session.get(bbb_instance + action + '&checksum=' + str(checksum), verify=False)
    result = json.loads(json.dumps(xmltodict.parse(result_xml.content)))
    return result['response']

def getURL(action):
    settings = loadSettings()["data"]
    bbb_instance = settings['settings']['bbbInstance']
    checksum = bbbGenerateChecksum(action)
    return bbb_instance + action + '&checksum=' + str(checksum)

def bbbGenerateChecksum(action):
    settings = loadSettings()["data"]
    bbb_secret = settings['settings']['bbbSecret']
    checksum = hashlib.sha1(action.replace('?','').encode('utf-8') + bbb_secret.encode('utf-8')).hexdigest()
    return checksum
