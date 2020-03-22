import os
import sys
from configparser import ConfigParser, Error

# Default config
APP_CONFIG_FILE = 'D:/Dev/py/etc/default.ini'
LOG_FORMAT = '%(asctime)s [{job_id}] %(name)s %(levelname)-8s %(lineno)-2d  %(message)s'


class Config:
    def __init__(self, file):
        self.data = None
        self._reload = True
        self.file = file

    def get(self, section, key, default=''):

        # load config file if data is not ready
        if self.data is None:
            if os.path.exists(self.file):
                self.data = ConfigParser()
                print("Load config file: ", self.file)
                self.data.read(self.file)
            else:
                print("cannot find the configuration file: ", self.file)

        # get value
        if self.data:
            try:
                return self.data.get(section, key)
            except Error as e:
                print(e)

        print(f'cannot find {section}/{key}, default value "{default}" used')
        return default


def reload(self):
    self.data = None


def get_env():
    # CONTEXT_ENV is set in test job runtime by the test framework
    # DEBUG_ENV is set by set_env() for debugging, it will be ignored in test jobs
    return os.environ.get('CONTEXT_ENV', '') or os.environ.get('DEBUG_ENV', '')


def set_env(env):
    """ only used for debugging. """
    os.environ['DEBUG_ENV'] = env


config = Config(APP_CONFIG_FILE)
