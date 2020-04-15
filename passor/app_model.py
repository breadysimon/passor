REST_ENVELOPED = 'EnvelopedRest'
REST = 'Rest'


class ApplicationModel:

    def __init__(self, envelope={}, type='Rest'):
        self.envelope = envelope or None
        self.type = type


class ApiModel:
    path = ''
    type = REST

    def __init__(self, app, path, method, request_json, response_json, type=''):
        self.path = path
        self.method = method
        self.request_json = request_json
        self.response_json = response_json
        self.app = app
        self.type = type or self.app.type
