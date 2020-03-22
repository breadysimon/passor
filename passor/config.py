import os
from configparser import ConfigParser

APP_CONFIG_FILE = '/etc/default.ini'


def get_config(section, key):
    cf = ConfigParser()
    cf.read(APP_CONFIG_FILE)
    return cf.get(section, key)


def get_env():
    # CONTEXT_ENV is set in test job runtime by the test framework
    # DEBUG_ENV is set by set_env() for debugging, it will be ignored in test jobs
    return os.environ.get('CONTEXT_ENV', '') or os.environ.get('DEBUG_ENV', '')


def set_env(env):
    """ only used for debugging. """
    os.environ['DEBUG_ENV'] = env
