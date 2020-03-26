import logging

import pytest
import requests_mock

from passor import config
from passor.api import Application
from passor.logging import rootLogger

logger = rootLogger.getChild(__name__)
logger.setLevel(logging.DEBUG)

APP_CONFIG='''
responseTemplate:
  fields:
    code: status
    msg: retMsg
    data: data
  successCode: SUCCESS
codeGeneration:
  snakeCaseStyle: false
  functionNameDepth: 1
environments:
  sit:
    apiRoot: https://sit-console.ctcfin.com
    dbConnection: sqlite:///db.sqlite
  uat:
    apiRoot: https://uat-console.ctcfin.com
    dbConnection:
      db0: sqlite:///db.sqlite
      db1: sqlite:///db1.sqlite

'''
API_SPEC_1='''
path: aaa/bbb/xxx
response:
  AAA: {x: 1, y: '2'}
'''

@pytest.fixture
def api():
    app = Application(APP_CONFIG)
    config.set_env('sit')
    api0 = app.create_api_client(API_SPEC_1)
    yield api0


class MyMock(requests_mock.Mocker):
    def __init__(self, **kwargs):
        super().__init__()
        body = dict(status='SUCCESS', retMsg='ok', data={})
        body.update(kwargs)
        if 'all' in kwargs:
            if kwargs['all'] == None:
                self.request(requests_mock.ANY, requests_mock.ANY, text='')
            else:
                self.request(requests_mock.ANY, requests_mock.ANY, text=kwargs['all'])
        elif 'http' in kwargs:
            self.request(requests_mock.ANY, requests_mock.ANY, json=body, status_code=kwargs['http'])
        else:
            self.request(requests_mock.ANY, requests_mock.ANY, json=body)


def test_assertions(api):
    with MyMock(data=dict(x=1, y='2', z='0000aaaa111', u=dict(v=[5, 6, 7], w=dict(x=9)))) as m:
        api.c_断言测试1() \
            .check_ok() \
            .check_values('响应应该符合预期', x=1) \
            .check_values(x=1, y='2', z='%aaa', code='SUCCESS', msg='ok') \
            .check_keys('x', 'y', 'z') \
            .check_by_example('AAA') \
            .check_by_example('Jinja2') \
            .check_by_example('多层JSON')

        with pytest.raises(AssertionError) as ex:
            api.check_by_example('多层JSON不一致')
        assert '应该包含于' in str(ex.value)

        api.c_断言测试2() \
            .check_by_example() \
            .check_values(x=1, y='2', z='%aaa', code='SUCCESS', msg='ok')

    with MyMock(status='FAIL'):
        with pytest.raises(AssertionError, match=r"应该{'code': 'SUCCESS'}"):
            api.c_断言测试2().check_ok()

    with MyMock(http=201, status='0000'):
        api.c_断言测试2() \
            .check_ok(http=201, code='0000')
