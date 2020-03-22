import os

from passor.config import config, set_env, get_env


def test_get():
    assert config.get('test', 'dummy') == '123', 'should parse and get value from the file'
    assert config.get('test', 'dummy', 'ddd') == '123', 'should parse and get value from the file'

    assert config.get('sec1', 'dummy', 'ddd') == 'ddd', 'when config is missing, should get default value'

    assert config.get('test', 'key1') == '', 'when key is missing, should get empty value'
    assert config.get('sec1', 'dummy') == '', 'when section is missing, should get empty value'

    tmp = config.file
    try:
        config.file = 'not_exist.ini'
        assert config.get('test', 'dummy') == '', 'when config file is missing, should get empty value'
    finally:
        config.file = tmp


def test_set_env():
    set_env('sit')
    assert get_env() == 'sit', 'when not running in test platform, the debug env setting should be used.'
    os.environ['CONTEXT_ENV'] = 'uat'
    assert get_env() == 'uat', 'when running in test platform, env should be set by runtime environment.'
