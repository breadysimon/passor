import json
import os
import re
import sys
from urllib.parse import urlparse, parse_qs

from box import Box
from simplejson import JSONDecodeError

from passor.config import get_env
from passor.logging import rootLogger
from passor.template import Template

logger = rootLogger.getChild(__name__)

REQ_DB_POST = 'DB后取'
REQ_DB_INIT0 = 'DB初始0'
REQ_DB_INIT1 = 'DB初始1'
REQ_DB_INIT2 = 'DB初始2'
REQ_DB_INIT3 = 'DB初始3'
REQ_DB_PRE = 'DB预取'
REQ_RESP = '响应'
REQ_ARG = '自定义参数'
REQ_STORE_RESP = '存值'
REQ_PARM = '参数'
REQ_REQ = '请求'
REQ_FORM = '表单'
REQ_UPLOAD = '上传'
REQ_URI = '路径'
REQ_METHOD = '方法'
REQ_FORMAT = '格式'
REQ_ENVELOP = '封装'

CFG_DB_URI = 'DB连接'
CFG_BASE_URI = 'API根路径'
CFG_CODE = '代码生成'
CFG_ENV = '环境配置'
CFG_RESPONSE = '响应模板'
CFG_API_SPEC = '接口声明'


def _convert_json_string_to_json(s):
    if isinstance(s, str):
        js = s.strip()
        if js.startswith('{') or js.startswith('['):
            s = json.loads(js)
    return s


class ApiRequest:
    def __init__(self, ctx, config, spec, name, sub_name=''):
        # 请求的全局对象
        self.yaml_file = ''
        self.config = config
        self.context = ctx
        # TODO: 定义spec对象,封装配置合并等操作
        self.name = name

        # 缺省配置
        self.method = 'post'
        self.uri = ''
        self.body = ''
        self.form = ''
        self.upload = ''
        self.params = {}
        self.store = {}
        self.args = ''  # TODO: 用dict
        self.response = {}
        self.db_pre = {}
        self.db_init0 = {}
        self.db_init1 = {}
        self.db_init2 = {}
        self.db_init3 = {}
        self.db_post = {}
        self.format = {}
        self.envelop = {}
        if CFG_RESPONSE in self.config:
            self.envelop = self.config[CFG_RESPONSE]

        # 状态值存储
        self.arg_values = {}
        self.db_values = {}
        self.request_body = {}
        self.header_values = {}
        self.request_result = None
        self.query_path = self.uri
        self.query_params = {}
        self.verbose = False
        self.pre_func = None

        # 按接口声明和子声明初始化
        self.update(spec)
        if sub_name:
            self.update(spec[REQ_REQ][sub_name])

    def update(self, spec):
        """从接口声明更新对象. 因为可以定义子声明, 产生的定义需要合并.
        子声明中各属性,部分缺省使用父节点,部分覆盖父节点,部分清零, 所以合并的逻辑比较复杂.
        """
        if isinstance(spec, str):
            # 如果只声名了一个字符串,则缺省赋值给request body
            self.body = spec
        else:
            # 必须重新声名的,缺省置为'', 否则缺省值来自上级节点
            for attr in ['body']:
                setattr(self, attr, '')

            for yaml_item in spec:
                attr = self._config_name_to_attr_name(yaml_item)

                if attr in ['method', 'uri', 'body', 'form', 'upload', 'args', 'response', 'envelop']:
                    # 新值覆盖
                    v = spec[yaml_item]
                    if v is None:
                        v = ''
                    setattr(self, attr, v)
                else:
                    # 与缺省值进行dict合并
                    v = getattr(self, attr)
                    logger.debug(f'{yaml_item},current value: {v}, new value: {spec[yaml_item]}')
                    setattr(self, attr, {**v, **spec[yaml_item]})

    def _config_name_to_attr_name(self, config_name):
        config_mapping = dict(method=REQ_METHOD, uri=REQ_URI, body=REQ_REQ,
                              upload=REQ_UPLOAD, form=REQ_FORM,
                              params=REQ_PARM, store=REQ_STORE_RESP,
                              args=REQ_ARG, response=REQ_RESP,
                              db_pre=REQ_DB_PRE, db_post=REQ_DB_POST,
                              db_init0=REQ_DB_INIT0, db_init1=REQ_DB_INIT1, db_init2=REQ_DB_INIT2,
                              db_init3=REQ_DB_INIT3,
                              format=REQ_FORMAT, envelop=REQ_ENVELOP)
        name_to_attr = dict((k, v) for v, k in config_mapping.items())
        return name_to_attr[config_name]

    def _extract_declared_args(self, kw):
        _a = {}
        logger.debug(f'kw args: {kw}, claimed: {self.args}')
        for x in self.args.split(','):
            defined_arg = x.strip()
            if defined_arg in kw:
                _a[defined_arg] = kw[defined_arg]
                # 这些参数不用于直接对响应结果的属性比对, 所以要从参数列表中删除
                del kw[defined_arg]
        logger.debug(f'get args: {_a}')
        self.arg_values = _a

    def run(self, headers=None, **kwargs):
        """
        :param json_template: 可以指定预先配置的命名模板，缺省按action命名。也可以直接提供json对象作为模板。
        :param headers:
        :param kwargs: 添加到模板中的参数(仅支持json对象第一层)
        :return: self
        """
        logger.debug(f'api func, headers: {headers}, kw: {kwargs}')
        self._init0_with_db_query(kwargs)
        self._render_kwargs(kwargs)
        self._init1_with_db_query(kwargs)
        self._extract_declared_args(kwargs)
        self._init2_with_db_query(kwargs)
        self._parse_uri(kwargs)
        self._prepare_request_data(kwargs)
        self.header_values = headers
        if self.pre_func:
            self.pre_func()
        url = f'{self.config[CFG_BASE_URI]}/{self.query_path}'
        if self.verbose:
            logger.info(f'{self.name}: Request \n'
                        f'{self.method.upper()} {url}\n'
                        f'params: {self.query_params}\n'
                        f'body:\n{json.dumps(self.request_body, indent=4, ensure_ascii=False)}')
        if self.upload:
            files = self._prepare_upload_files(kwargs)
            result = self.context.session.post(
                url=url,
                data=self.request_body,
                files=files,
                params=self.query_params,
                headers=headers
            )
        elif self.form:
            result = self.context.session.post(
                url=url,
                data=self.request_body,
                params=self.query_params,
                headers=headers
            )
        else:
            result = self.context.session.request(
                method=self.method,
                url=url,
                json=self.request_body,
                params=self.query_params,
                headers=headers
            )

        if self.verbose:
            try:
                s = json.dumps(result.json(), indent=4, ensure_ascii=False)
            except (TypeError, JSONDecodeError):
                s = result.text
            logger.info(f'{self.name}: Response \n'
                        f'{s}')

        self.fetch_db_data(self.db_post, kwargs)
        self.request_result = result
        return self

    def _prepare_request_data(self, kwargs):
        self.fetch_db_data(self.db_pre, kwargs)
        data = self.body or self.form
        try:
            data = self._render_json_template(data, kwargs)
        except(JSONDecodeError, json.decoder.JSONDecodeError) as e:
            if isinstance(data, str):
                data = self._render_str_template(data, kwargs)
            elif data is not None:
                raise e
        logger.debug(f'request data:{self.request_body}')
        self.request_body = data
        return data

    def _render_json_template(self, json_template, kwargs):
        if not isinstance(json_template, str):
            logger.debug(f'dump json for apply template vars: {json_template}')
            json_template = json.dumps(json_template)
        merged_vars = {**self.get_context_locals(kwargs)}
        data = Template(json_template).render_as_json(**merged_vars)
        if isinstance(data, dict):
            logger.debug(f'apply kwargs to data/*: {kwargs}')
            data.update(**kwargs)
        return data

    def _render_str_template(self, template, kwargs):
        merged_vars = {**self.get_context_locals(kwargs)}
        data = Template(template).render(**merged_vars)
        return data

    def _parse_uri(self, kwargs):
        uri_str = self.render_string(self.uri, kwargs)
        u = urlparse(uri_str)
        q = parse_qs(u.query)
        _merge_params(q, self.params, kwargs)
        self.query_path = u.path.lstrip("/")
        self.query_params = q

    def get_db_spec(self, db_spec, kwargs):
        for var_name, query in db_spec.items():
            db_name = ''
            table_name = var_name
            m0 = re.match(r'^\((.*)\)\s*(.*)', query)
            if m0:
                db_name = m0.group(1)
                if ':' in db_name:
                    db_name, table_name = db_name.split(':')
                query = m0.group(2)

            # 旧的处理格式, Depraciated
            m = re.match(r'(.*?)#(.*)', query)
            if m:
                table_name = m.group(1)
                if '@' in table_name:
                    table_name, db_name = table_name.split('@')
                query = m.group(2)

            if Template.is_template(query):
                query = self.render_string(query, kwargs)
            logger.debug(f'db params: var={var_name},table={table_name},db={db_name},query={query}')
            yield var_name, table_name, db_name, query

    def fetch_db_data(self, db_spec, kwargs):
        """
        从db中查询数据.
        键-值 分别是变量名和查询.
        如果不是select查询, 则写成'表名#过滤属性列表'格式, 如: users#name='foo',id=123,
        如果变量名就是表名,只需要写'过滤属性列表'.
        """
        logger.debug(f'db_spec: {db_spec}')
        for var_name, table_name, db_name, query in self.get_db_spec(db_spec, kwargs):
            db = self.context.db[db_name] if db_name else self.context.db
            if 'SELECT ' not in query.upper() and '=' in query:
                # 如果不是select语句且仅包含dict赋值列表
                filters = eval(self.render_string('${dict(' + query + ')}', kwargs))
                results = db.query(table_name, **filters)
            else:
                query = self.render_string(query, kwargs)
                results = db.execute(query).fetchall()

            self.db_values[var_name + "_all"] = results
            self.db_values[var_name] = results[0] if len(results) > 0 else None

    def render_string(self, t, kwargs={}):
        if Template.is_template(t):
            return Template(t).render(**self.get_context_locals(kwargs))
        return t

    def store_values(self):
        for k, v in self.store.items():
            self.context.globals.set_var(k, self.render_string('${' + str(v) + '}'))

    def get_context_locals(self, kwargs={}):
        """提取要存值的数据
              _a: 参数声名的变量
              _b: 请求body
              _c: cookie
              _d: DB查询数据
              _h0: 请求的headers
              _h: response/headers
              _m: response/message
              _n: api name
              _p: 请求参数
              _r: response/data
              _s: response/code
              _u: url
          """
        pre_defined_vars = dict(
            _a=self.arg_values or {},
            _b=self.request_body or {},
            _c=self.context.session.cookies if self.context.session else {},
            _d=self.db_values or {},
            _e=self.config or {},
            _h0=self.header_values or {},
            _h=self.request_result.headers if self.request_result else {},
            _m=self.get_response_data('msg'),
            _n=self.name,
            _p=self.query_params,
            _r=self.get_response_data(),
            _s=self.get_response_data('code'),
            _u=self.query_path or ''
        )
        merged = {**self.context.globals.get_all(), **pre_defined_vars, **kwargs}
        return merged

    def get_response_list(self):
        data = self.get_response_data()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list):
                    return v

    def get_response_data(self, field='data'):
        if self.request_result is None:
            return None

        envelop_mapping, data = self._normalize_response_data()

        if field in envelop_mapping.keys():
            # 如果查询字段是'响应模板'中定义了映射关系的保留字段, 则查表转换为真实字段
            return data[envelop_mapping[field]]
        else:
            # 对应字段来自data节点下级属性
            return data[envelop_mapping['data']][field]

    def get_expected_response(self, name, kwargs):
        pattern = json.dumps(self.response[name] if name else self.response)
        s = self.render_string(pattern, kwargs)
        js = json.loads(s)
        print(pattern, s, js)
        js = _convert_json_string_to_json(js)
        return js

    def _normalize_response_data(self):
        """把返回值统一为封装好的JSON
        """
        enveloped = True
        try:
            data = self.request_result.json()
        except ValueError:
            data = self.request_result.text
            enveloped = False

        if '字段' in self.envelop:
            mapping = self.envelop['字段']
        else:
            mapping = dict(code='code', msg='msg', data='data')
            enveloped = False

        if not enveloped:
            data = {
                mapping['code']: self.request_result.status_code,
                mapping['msg']: '',
                mapping['data']: data
            }
            logger.debug(f'generated envelop: {data}')
        return mapping, data

    def save_response_value(self, locator, var='', data_src=None, **kwargs):
        if var == '':
            var = locator
        if data_src is None:
            # 缺省从response中读取数据
            data_src = self.get_response_data()

        locator = '${' + str(locator) + '}'
        v = self.render_string(locator, {**data_src, **kwargs})
        self.context.globals.set_var(var, v)

    def save_response_values(self, *fields):
        for x in fields:
            self.context.globals.set_var(x, self.request_result.json()['data'][x])

    def _prepare_upload_files(self, kwargs):
        file_list = self._render_json_template(self.upload, kwargs)
        files = {}
        for k, v in file_list.items():
            full_path = v
            if not v.startswith('/'):
                print(self.__class__)
                full_path = os.path.join(os.path.dirname(self.context.definition.file), v)
            files[k] = open(full_path, 'rb')
        logger.debug(f'request files:{files}')
        return files

    def _render_kwargs(self, kwargs):
        for k, v in kwargs.items():
            kwargs[k] = self.render_string(v, kwargs)

    def _init0_with_db_query(self, kwargs):
        self.fetch_db_data(self.db_init0, kwargs)

    def _init1_with_db_query(self, kwargs):
        self.fetch_db_data(self.db_init1, kwargs)

    def _init2_with_db_query(self, kwargs):
        self.fetch_db_data(self.db_init2, kwargs)

    def _init3_with_db_query(self, kwargs):
        self.fetch_db_data(self.db_init3, kwargs)


class Definition:
    def __init__(self, cls, yaml=''):
        if yaml:
            data = Box.from_yaml(yaml)
        else:
            self.file = self.get_spec_file_name(cls)
            data = Box.from_yaml(filename=self.file)

        if CFG_API_SPEC in data:
            self.spec = data[CFG_API_SPEC]
        env = get_env()
        if CFG_ENV in data and env:
            data.update(data[CFG_ENV][env])
        self.config = {}
        for k, v in data.items():
            if k not in [CFG_API_SPEC, CFG_ENV]:
                self.config[k] = v

    @staticmethod
    def get_spec_file_name(cls):
        class_file_path = sys.modules[cls.__module__].__file__
        return re.sub('.py$', '.yaml', class_file_path)


class GlobalVariables:
    def __init__(self):
        self.vars = {}

    def set_var(self, name, value):
        if name.startswith('_'):
            raise Exception('保存的全局变量命名不能以"_"开头')
        self.vars[name] = value

    def get_var_str(self, name):
        return str(self.vars.get(name, None))

    def get_var(self, name):
        value = self.get_var_str(name)
        try:
            value = eval(value)
        except Exception as ex:
            logger.warning(f'fail to eval {value},{ex}')
        return value

    def del_var(self, name):
        if name in self.vars:
            del self.vars[name]

    def clear(self):
        self.vars = {}

    def get_all(self):
        return self.vars


def _merge_params(x, y, kw):
    """合并两个params字典,元素可能是List,相同key的需要合并成list"""
    for k, v in y.items():
        if k in x:
            if isinstance(x[k], list):
                if isinstance(v, list):
                    x[k].extend(v)
                else:
                    x[k].append(v)
            else:
                x[k] = [x[k], v]
        else:
            x[k] = v

    # 把仅有一个元素的值还原为非数组
    compress_params(x)

    # 如果调用接口时直接给定了参数值, 以给定的为准
    for k, v in list(kw.items()):
        if k in x:
            x[k] = v
            del kw[k]


def compress_params(x):
    for k, v in x.items():
        if isinstance(v, list) and len(v) == 1:
            x[k] = v[0]
