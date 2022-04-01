import os
import yaml
import logging

class SchoolManager():
    def __init__(self):
        self.school = 'default-school'

    def load_custom_fields(self):
        config = f'/etc/linuxmuster/sophomorix/{self.school}/custom_fields.yml'
        self.custom_fields = {}
        if os.path.isfile(config):
            try:
                with open(config, 'r') as f:
                    self.custom_fields = yaml.load(f, Loader=yaml.SafeLoader)
            except Exception as e:
                logging.error(f"Could not load custom fields config: {e}")

    def switch(self, school):
        # Switch to another school
        self.school = school
        self.load_custom_fields()