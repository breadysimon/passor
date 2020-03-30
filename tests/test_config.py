import os

from passor.config import Config, set_env, get_env


def test_get():
    config = Config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'examples', 'config.ini'))

    assert config.get('test', 'dummy') == '123', 'should parse and get value from the file'
    assert config.get('test', 'dummy', 'ddd') == '123', 'when config found in file, should ignore default value'
    assert config.get('sec1', 'dummy', 'ddd') == 'ddd', 'when config is missing, should use default value'
    config.file = ""
    assert config.get('test', 'dummy') == '123', 'when data is loaded, should reuse the data'

    # abnormal args
    assert config.get('test', 'key1') is config.get('', 'key1') is config.get('test', '') is \
           config.get('sec1', 'dummy') is None, 'when section is missing, should get empty value'

    conf_err = Config('not_exist.ini')
    assert conf_err.get('test', 'dummy') is None, 'when config file is missing, should get empty value'

    config.add('sec2', 'key2', '1', 'TMP_CF')
    assert config.get('sec2', 'key2') == '1', 'when preset, should use preset default value'

    os.environ['TMP_CF'] = 'aaa'
    assert config.get('sec2', 'key2') == 'aaa', 'when env name is preset and os env is set, should use environ value'


def test_set_env():
    bkup = os.environ.get('CONTEXT_ENV','')
    os.environ['CONTEXT_ENV'] = ''
    set_env('sit')
    assert get_env() == 'sit', 'when not running in test platform, the debug env setting should be used.'
    os.environ['CONTEXT_ENV'] = 'uat'
    assert get_env() == 'uat', 'when running in test platform, env should be set by runtime environment.'
    os.environ['CONTEXT_ENV'] = bkup