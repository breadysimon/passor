import pytest

from passor.app_model import ApplicationModel, ApiModel, REST_ENVELOPED
from passor.tester import ApiTester
from tests.test_api import MyMock


@pytest.fixture
def tester():
    app = ApplicationModel(
        type=REST_ENVELOPED,
        envelope=dict(
            fields=dict(code='status', msg='retMsg', data='data'),
            successCode='SUCCESS'
        )
    )
    api = ApiModel(app, '/test', 'post', '', '')
    t = ApiTester('http://localhost:8080')
    t.add_api('example', api)
    yield t


def test_generic(tester):
    with MyMock(data=dict(x=1, y='2', z='0000aaaa111', u=dict(v=[5, 6, 7], w=dict(x=9)))) as m:
        tester.invoke('example') \
            .check_ok() \
            .check_data(x=1, y='2', z='%aaaa', u=dict(v=[5, 6, 7], w=dict(x=9))) \
            .check_status(code='SUCCESS', msg='ok')
