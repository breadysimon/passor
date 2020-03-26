import json
import re

from jinja2 import Environment

from passor import plugins
from passor.logging import rootLogger

logger = rootLogger.getChild(__name__)


class Template:
    def __init__(self, t):
        self.env = Environment('<%', '%>', '${', '}', '$#')
        self.template_string = t

    @staticmethod
    def is_template(s):
        if isinstance(s, str):
            return re.search(r'(\${|<%)', s)
        return False

    def render(self, **kw):
        # TODO: 提前处理 **kw合并时变量重名异常
        if Template.is_template(self.template_string):
            logger.debug(f'template: {self.template_string}'.replace('\n', r'\n'))
            self.load_plugins()
            tmpl = self.env.from_string(self.template_string)
            js = tmpl.render(**kw)
            logger.debug(f'rendered template: {js}'.replace('\n', r'\n'))
            return js
        else:
            return self.template_string

    def render_as_json(self, **kw):
        js = self.render(**kw)
        if js.strip() == '':
            return {}
        else:
            return json.loads(js)

    def load_plugins(self):
        for k, v in plugins.__dict__.items():
            if k.startswith('filter_'):
                name = re.sub(r'filter_', '', k)
                self.env.filters[name] = v
            elif k.startswith('cf_'):
                name = re.sub(r'cf_', '', k)
                self.env.globals[name] = v
