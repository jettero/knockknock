# coding: utf-8

import os
from click_config_file import configobj_provider

class Provider(configobj_provider):
    def __init__(self):
        super().__init__(False, 'synkk')

    def __call__(self, file_path, cmd_name):
        try:
            return super().__call__(os.path.expanduser(file_path), cmd_name)
        except KeyError:
            return dict()
