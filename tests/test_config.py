import os

from passor import config


def test_get_config():
    assert config.get_config('a', 'x') == '123', 'should be able to parse and get value from config file'


def test_set_env():
    config.set_env('sit')
    assert config.get_env() == 'sit', 'when not running in test platform, the debug env setting should be used.'
    os.environ['CONTEXT_ENV'] = 'uat'
    assert config.get_env() == 'uat', 'when running in test plateform, env should be set by runtime environment.'
