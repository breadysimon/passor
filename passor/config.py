import os
import sys
from configparser import ConfigParser, Error

# Default config
APP_CONFIG_FILE = 'D:/Dev/py/etc/default.ini'
LOG_FORMAT = '%(asctime)s [{job_id}] %(name)s %(levelname)-8s %(lineno)-2d  %(message)s'


class Config:
    def __init__(self, file):
        self.data = None
        self.reload = True
        self.file = file

    def get(self, section, key, default=''):
        if os.path.exists(self.file):
            if self.reload:
                self.data = ConfigParser()
                print("Load config file: ", self.file)
                self.data.read(self.file)
                self.reload = False
            try:
                return self.data.get(section, key)
            except Error as e:
                print(e)
        else:
            print("Can't find the configuration file: ", self.file)
        return default


def get_env():
    # CONTEXT_ENV is set in test job runtime by the test framework
    # DEBUG_ENV is set by set_env() for debugging, it will be ignored in test jobs
    return os.environ.get('CONTEXT_ENV', '') or os.environ.get('DEBUG_ENV', '')


def set_env(env):
    """ only used for debugging. """
    os.environ['DEBUG_ENV'] = env


config = Config(APP_CONFIG_FILE)
