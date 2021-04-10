import os
from pathlib import PurePath
from app.tools.io import path_create

conf = {
    'DB_PATH': './assets/data/db.sqlite3'
}


def clean_startup():
    for item in conf:
        if item.endswith('PATH'):
            path_create(conf[item], is_file=True)


class Config(object):
    def __init__(self):
        self._config = conf

    def get_property(self, property_name):
        if property_name not in self._config.keys():
            return None
        return self._config[property_name]


class AssetConfig(Config):
    @property
    def db_path(self):
        return self.get_property('DB_PATH')
