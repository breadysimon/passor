import os
from configparser import ConfigParser, Error


# Default config


class Config:
    def __init__(self, file):
        self.data = None
        self.file = file
        self.preset = {}

    def get(self, section, key, default=None):
        k = f'{section}/{key}'
        if k in self.preset:
            e = self.preset[k]['environ']
            if e in os.environ:
                return os.environ[e]
            if default is None:
                default = self.preset[k]['default']

        # load config file if data is not ready
        if self.data is None:
            print("Load config file: ", self.file)
            if os.path.exists(self.file):
                self.data = ConfigParser()
                self.data.read(self.file)
            else:
                print("cannot find the configuration file: ", self.file)

        # get value
        if self.data:
            try:
                v = self.data.get(section, key)
                print(f'got config {section}/{key} = {v}')
                return v
            except Error as e:
                print(e)

        print(f'cannot find {section}/{key}, default value "{default}" used')
        return default

    def add(self, section, key, default, environ):
        """ configuration priorities: os env variable > config file > argument default > preset default. """
        k = f'{section}/{key}'
        self.preset[k] = dict(default=default, environ=environ)

    def set(self,section,key,value):
        self.data.set(section,key,value)

    def reload(self):
        self.data = None


def get_env():
    # CONTEXT_ENV is set in test job runtime by the test framework
    # DEBUG_ENV is set by set_env() for debugging, it will be ignored in test jobs
    return os.environ.get('CONTEXT_ENV', '') or os.environ.get('DEBUG_ENV', '')


def set_env(env):
    """ only used for debugging. """
    os.environ['DEBUG_ENV'] = env


def get_config_file():
    default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'etc', 'default.ini')
    v = os.environ.get('PASSOR_CONFIG', default)
    return v


config = Config(get_config_file())
