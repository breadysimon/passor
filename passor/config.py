import os
from configparser import ConfigParser

APP_CONFIG_FILE = '/etc/passor.ini'


def get_config(section, key):

    cf = ConfigParser()
    cf.read(APP_CONFIG_FILE)
    return cf.get(section, key)


def get_env():
    e = os.environ.get('CONTEXT_ENV', '')
    if e:
        return e
    else:
        return os.environ.get('DEBUG_ENV', '')


def set_env(env):
    os.environ['DEBUG_ENV'] = env
