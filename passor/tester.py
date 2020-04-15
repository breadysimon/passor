import requests


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
            return CheckerFactory.get(api.type, api, result)


class CheckerFactory:
    @staticmethod
    def get(name, api, result):
        if name == 'Rest':
            return RestResultChecker(api, result)
        elif name == 'EnvelopedRest':
            return EnvelopedResultChecker(api, result)
        return None


class RestResultChecker:
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

    def check_status(self, status_code=200, **kwargs):
        assert self.result.status_code == status_code

    def check_data(self, should='', **kwargs):
        assertion = should or f'should have {kwargs}'
        for x in kwargs:
            v = self.data[x]
            expected = kwargs[x]
            if isinstance(expected, str) and expected.startswith('%'):
                assert expected.strip('%') in v, assertion
            else:
                assert v == expected, assertion
        return self


class EnvelopedResultChecker(RestResultChecker):
    def resolve_data(self):
        r = self.result.json()
        fields = self.api_model.app.envelope['fields']
        self.data = r[fields['data']]
        self.success_code = self.api_model.app.envelope['successCode']
        self.status = dict(code=r[fields['code']], msg=r[fields['msg']])

    def check_status(self, status_code=200, **kwargs):
        assert self.result.status_code == status_code
        if 'msg' in kwargs:
            assert self.status['msg'] == kwargs['msg']
        expected = self.success_code
        if 'code' in kwargs:
            expected = kwargs['code']
        assert self.status['code'] == expected