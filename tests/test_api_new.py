import pytest
import requests

from tests.test_api import MyMock


class ApiTester:
    apis = {}
    results = []

    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.session = requests.Session()

    def add_api(self, name, api):
        self.apis[name] = api

    def invoke(self, name):
        api = self.apis[name]
        if api.method == 'post':
            result = self.session.post(
                url=self.base_uri + api.path,
                data=api.request_json  # ,files=files, #params=self.query_params, #headers=headers
            )
            self.results.append(result)
            if api.app.enveloped:
                return EnvelopedResultChecker(api, result)
            else:
                return ResultChecker(api, result)


class ResultChecker:
    data = None

    def __init__(self, api, result):
        self.api_model = api
        self.result = result

        self.expected_http_status_code = 200

        self.resolve_data()

    def resolve_data(self):
        self.data = self.result.json()

    def check_ok(self):
        assert self.result.status_code == self.expected_http_status_code
        return self

    def check_values(self, should='', **kwargs):
        assertion = should or f'should have {kwargs}'
        for x in kwargs:
            v = self.data[x]
            expected = kwargs[x]
            if isinstance(expected, str) and expected.startswith('%'):
                assert expected.strip('%') in v, assertion
            else:
                assert v == expected, assertion
        return self


class EnvelopedResultChecker(ResultChecker):
    def resolve_data(self):
        self.data = self.result.json()['data']


class ApiModel:
    path = ''

    def __init__(self, app, path, method, request_json, response_json):
        self.path = path
        self.method = method
        self.request_json = request_json
        self.response_json = response_json
        self.app = app


class Application:
    def __init__(self, enveloped=False):
        self.enveloped = enveloped


@pytest.fixture
def tester():
    app = Application(enveloped=True)
    api = ApiModel(app, '/test', 'post', '', '')
    t = ApiTester('http://localhost:8080')
    t.add_api('example', api)
    yield t


def test_generic(tester):
    with MyMock(data=dict(x=1, y='2', z='0000aaaa111', u=dict(v=[5, 6, 7], w=dict(x=9)))) as m:
        tester.invoke('example') \
            .check_ok() \
            .check_values(x=1, y='2',z='%aaaa')
