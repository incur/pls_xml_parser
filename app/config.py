import os
from pathlib import PurePath
from app.tools.io import path_create

conf = {
    'DB_PATH': './assets/data/db.sqlite3',
    'APP_LOG_PATH': './assets/log/app.log',
    'INFO_LOG_PATH': './assets/log/app_info.log',
    'ERROR_LOG_PATH': './assets/log/app_error.log'
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


class LogConfig(Config):
    @property
    def app_log_path(self):
        return self.get_property('APP_LOG_PATH')

    @property
    def info_log_path(self):
        return self.get_property('INFO_LOG_PATH')

    @property
    def error_log_path(self):
        return self.get_property('ERROR_LOG_PATH')
