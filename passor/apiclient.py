import json
import os
import re

from box import Box

from passor.config import config
from passor.logging import rootLogger

logger = rootLogger.getChild(__name__)


class ServiceCallerFactory:
    apps = {}

    def __init__(self, config_home):
        self.config_home = config_home

    def get_caller(self, name, env):
        f = os.path.join(self.config_home, f'app_{name}.yaml')
        spec = Box.from_yaml(filename=f)
        app = Application(name, spec, env)
        return app


class Application:
    def validate_spec(self, spec):
        valid, msg = True, ""
        if self.L.CFG_ENV not in spec:
            valid = False
            msg = 'no environments config found'
        elif self.env not in spec.env:
            valid = False
            msg = f'"{self.env} is not found in environments"'

        return valid, msg

    def __init__(self, name, spec, env):
        self.name = name
        self.env = env
        self.L = config.get_locale('en')
        self.load_spec(spec)

    def load_spec(self, spec):
        valid, msg = self.validate_spec(spec)
        if not valid:
            logger.error(f'invalid application config: {msg}')
            return

        self.enveloped = self.L.CFG_RESPONSE in spec
        if self.enveloped:
            self.response_fields = spec[self.L.CFG_RESPONSE][self.L.CFG_FIELDS]
            self.success_code = spec[self.L.CFG_RESPONSE][self.L.CFG_SUCC_CODE]
        self.environmental_config = spec[self.L.CFG_ENV][self.env]

    def create_api_client(self, js):
        return ApiClient(self, js)


class ApiClient:
    def __init__(self, app, js):
        self.app = app
        self.config = json.loads(js)


def _is_json(p):
    try:
        json.dumps(p)
        return True
    except TypeError as e:
        logger.debug(f'check if is a json string: {e}')
        return False


class Context:
    def __init__(self, session=None, global_vars=None, db=None, definition=None):
        self.session = session
        self.db = db
        self.globals = global_vars
        self.definition = definition


class ApiSuite:
    def __init__(self, yaml=''):
        self.config = data.config
        self._init_db_connections()
        self.spec = data.spec
        self.context = Context(
            session=Session(),
            global_vars=GlobalVariables(),
            definition=data,
            db=self.db)
        self.source_code = CodeGenerator(self.config, self.spec, self.__class__)
        self._init_functions()
        self.last_request = None
        self._verbose = False

    def clear(self):
        self.context.session = Session()
        self.context.globals.clear()

    def get_processor(self, kind, func_name, name):
        for fn in [re.sub('^c_', '', func_name), name]:
            func = f'_{kind}_{fn}'
            if hasattr(self, func):
                logger.info(f'execute {kind}-processor: {func}')
                return getattr(self, func)
        return None

    def _create_func(self, func_name, name):
        def func(sub_name='', **kwargs):
            logger.debug(f'call func: {name}:{sub_name}')
            pre_func = self.get_processor('pre', func_name, name)
            api_func = ApiRequest(self.context, self.config,
                                  self.spec[name], name, sub_name)
            api_func.verbose = self._verbose
            api_func.pre_func = pre_func
            self.last_request = api_func.run(**kwargs)

            # 请求不成功时不会调用后置处理器, TODO: 如何处理HTTP 200 OK 但code是出错码的情况?
            # if rec.response.status_code == 200:

            post_func = self.get_processor('post', func_name, name)
            if post_func:
                post_func()

            self.last_request.store_values()

            return self

        return func

    def attach_to(self, obj):
        self.context.session = obj.context.session
        self.context.globals = obj.context.globals
        return self

    def verbose(self, b):
        self._verbose = b
        return self

    def check_ok(self, http=200, code=None):
        ao = self.last_request
        assert ao.request_result.status_code == http
        if '成功状态码' in ao.envelop:
            ok = ao.envelop.get('成功状态码', None) if code is None else code
            if ok is not None:
                assert self.check_values(code=ok)

        return self

    def check_keys(self, *args, nest=False, parent=''):
        resp = self.last_request.get_response_data()
        if nest:
            logger.warning("nest arguement is depresiated, use 'parent=<jsonpath>' instead!")
            for x in args:
                flag = self._check_keys_in_iterator(str=x, dict_data=resp)
                assert flag == True, f"应该存在以下字段:{args}"
        else:
            data = [resp]
            if parent:
                exp = parse(parent)
                data = [m.value for m in exp.find(resp)]
            for d in data:
                for x in args:
                    assert x in d, f"应该存在以下字段:{args}"
        return self

    def _check_keys_in_iterator(self, str, dict_data):
        if isinstance(dict_data, dict):
            self.flag = str in dict_data
            if not self.flag:
                for k, v in dict_data.items():
                    self._check_keys_in_iterator(str, v)
                    if self.flag:
                        break
        elif isinstance(dict_data, list):
            if not self.flag:
                for i in dict_data:
                    self._check_keys_in_iterator(str, i)
                    if self.flag:
                        break
        else:
            if str == dict_data:
                self.flag = True
        return self.flag

    def check_by_example(self, name='', _id='', _table='', **kwargs):
        lr = self.last_request
        logger.debug(f'last called: {lr}')

        if _table:
            data_list = lr.get_response_list()
            for x in data_list:
                db_row = self.db.get_row(_table, x[_id])  # lr.db_get(_table, x[_id])
                kwargs["_i"] = db_row
                expected_response = lr.get_expected_response(name, kwargs)
                logger.debug(f'expected: {expected_response}')
                self.assert_containing_expected_json(expected_response, x)
        else:
            expected_response = lr.get_expected_response(name, kwargs)
            logger.debug(f'expected: {expected_response}')
            if _is_json(expected_response):
                v = self.last_request.get_response_data()
                self.assert_containing_expected_json(expected_response, v)
            else:
                assert lr.response.text == str(expected_response)

        return self

    def check_by_template(self, template, expected):
        v = self.get_value_by_template(template)
        assert v == expected
        return self

    def get_value_by_template(self, template):
        return self.last_request.render_string(template)

    def get_dict_by_template(self, template):
        return dict(eval(self.get_value_by_template(template)))

    def get_list_by_template(self, template):
        return list(eval(self.get_value_by_template(template)))

    def get_ctx_value(self, name):
        return self.last_request.get_context_locals().get(name)

    def check_values(self, should='', **kwargs):
        assertion = should or f'应该{kwargs}'
        for x in kwargs:
            v = self.last_request.get_response_data(field=x)
            expected = kwargs[x]
            if isinstance(expected, str) and expected.startswith('%'):
                assert expected.strip('%') in v, assertion
            else:
                assert v == expected, assertion
        return self

    def check_golden_file(self, file_path, template='', msg=None):
        ss = self.get_value_by_template(template)
        assert_golden(file_path, ss, msg)

        return self

    def check_golden_template(self, file_path, name='', msg=None):
        # TODO: 实现在YAML中预定义模板
        template = ''
        self.check_golden_file(file_path, template, msg=msg)

        return self

    def set_global(self, name, value):
        self.context.globals.set_var(name, value)
        return self

    def get_global(self, name):
        return self.context.globals.get_var(name)

    def get_global_str(self, name):
        return self.context.globals.get_var_str(name)

    def del_global(self, name):
        self.context.globals.del_var(name)
        return self

    def get_response(self):
        return self.last_request.request_result

    def save_response_value(self, locator, var='', data_src=None, **kwargs):
        self.last_request.save_response_value(locator, var, data_src, **kwargs)

    def save_response_values(self, *fields):
        self.last_request.save_response_values(*fields)


def assert_golden(file, data_string, msg=None):
    if os.path.isfile(file):
        # 如果文件已经存在, 断言data_string与文件一致
        with open(file, 'rb') as f:
            golden = f.read()
            assert _diff_from_golden(data_string, golden, file) == '', msg
    else:
        # 如果文件不存在, 就把当前data_string保存为测试基准
        _write_golden_file(file, data_string)


def _diff_from_golden(data_string, expected, file):
    """
    与GoldenFile比对,如果不一致,则将内容保存在以时间为后缀的文件里
    """
    file_current = re.sub('.gf$', datetime.datetime.now().strftime('%y%m%d%H%M%S') + '.gf', file)
    if not isinstance(data_string, str):
        data_string = str(data_string, encoding='utf-8')
    diff_result = udiff(str(expected, encoding='utf-8').split('\n'),
                        data_string.split('\n'),
                        os.path.basename(file),
                        os.path.basename(file_current))
    if diff_result != '':
        _write_golden_file(file_current, data_string)
    return diff_result


def _write_golden_file(file, data_string):
    path = os.path.dirname(file)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(file, 'wb+') as f:
        logger.warning(f'generate golden file: {file}')
        f.write(data_string.encode('utf-8'))
