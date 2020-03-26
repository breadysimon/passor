import json
import re

from tabulate import tabulate
from jmespath import search


def filter_list_table(js):
    if not isinstance(js, list):
        for k, v in js.items():
            if isinstance(v, list):
                js = v
                break
    return tabulate(js, headers='keys', tablefmt='presto')  # fancy_grid


def filter_as_table(js):
    return tabulate([js], headers='keys', tablefmt='presto')  # fancy_grid


def filter_as_json(js):
    return json.dumps(js, indent=4, ensure_ascii=False)


def filter_delattr(js, *args):
    return {k: v for k, v in js.items() if k not in args}


def filter_attrs(js, *args):
    return {k: v for k, v in js.items() if k in args}


def filter_find(lst, **kwargs):
    def check(x):
        return all([(k in x and x[k] == v) for k, v in kwargs.items()])

    return next(x for x in lst if check(x))


def filter_regex_replace(s, find, replace):
    return re.sub(find, replace, s)


def filter_jsonpath(js, path):
    return search(path, js)


def filter_esc(s):
    return s.encode('unicode_escape').decode('utf-8')

