import logging
import logging.handlers
from app.config import LogConfig

config = LogConfig()


class LogFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno <= self.__level


def logg_handlers(verbose):
    app_level = logging.NOTSET
    info_level = logging.INFO
    error_level = logging.WARNING
    if verbose:
        console_level = logging.FATAL
    else:
        console_level = logging.INFO

    app_log_handler = logging.handlers.RotatingFileHandler(config.app_log_path, maxBytes=2000000, backupCount=10)
    app_log_handler.setLevel(app_level)

    info_log_handler = logging.handlers.RotatingFileHandler(config.info_log_path, maxBytes=2000000, backupCount=5)
    info_log_handler.setLevel(app_level)
    info_log_handler.addFilter(LogFilter(info_level))

    error_log_handler = logging.handlers.RotatingFileHandler(config.error_log_path, maxBytes=2000000, backupCount=2)
    error_log_handler.setLevel(error_level)

    console_log_handler = logging.StreamHandler()
    console_log_handler.setLevel(console_level)
    console_log_handler.addFilter(LogFilter(console_level))

    f = logging.Formatter('%(asctime)s :: %(levelname)s :: %(name)s :: func:%(funcName)s :: %(message)s')
    app_log_handler.setFormatter(f)
    info_log_handler.setFormatter(f)
    error_log_handler.setFormatter(f)
    console_log_handler.setFormatter(f)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    root.addHandler(app_log_handler)
    root.addHandler(info_log_handler)
    root.addHandler(console_log_handler)
    root.addHandler(error_log_handler)
