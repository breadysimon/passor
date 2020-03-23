import logging
import os
import urllib
from logging.handlers import RotatingFileHandler
from urllib.parse import urlencode

import requests
from pygelf import GelfTcpHandler

from passor.config import config


class GELFLevel:
    DEBUG = 7
    INFO = 6
    WARNING = 4
    ERROR = 3
    CRITICAL = 2


# def load_config(filename):
#     cf = ConfigParser()
#     data = cf.read(filename)
#     if len(data) == 0:
#         raise ValueError(f'加载配置文件失败,filename={filename}')
#
#     if os.environ.get('DEBUG', default='').upper() == 'TRUE':
#         cf.set('log', 'DEBUG', 'True')
#
#     cf.add_section('runtime')
#
#     return cf

def get_job_id():
    return int(os.environ.get('JOB_ID', '0'))


def init_logger(name=None):
    job_id = get_job_id()
    logger = logging.getLogger(name)

    # TODO: log level
    logger.setLevel(logging.DEBUG)

    if 3 > len(logger.handlers):
        fmt = config.get('log', 'LOG_FORMAT')
        formatter = logging.Formatter(fmt.format(job_id=job_id))

        # Standard handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # File handler
        f = config.get('log', 'LOG_FILE')
        log_file = f.format(job_id=job_id)
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handler_file = RotatingFileHandler(filename=log_file, maxBytes=10 * 1024 * 1024, backupCount=7)
        handler_file.setFormatter(formatter)
        logger.addHandler(handler_file)

        # Graylog handler
        logger.addHandler(GelfTcpHandler(host=config.get_config('log', 'GRAYLOG_SERVER'),
                                         debug=True,
                                         port=config.get_config('log', 'GRAYLOG_TCP_PORT'),
                                         trace_id=job_id,
                                         source_tag='passor',
                                         include_extra_fields=True,
                                         ))

    return logger


def get_logger(name=None):
    return logging.getLogger(name)


def query_graylog(job_id, level=3, range=300, limit=150, keyword=''):
    """"""
    host = config.get('log', 'GRAYLOG_SERVER')
    port = config.get('log', 'GRAYLOG_HTTP_PORT')
    user = config.get('log', 'GRAYLOG_USER')
    password = config.get('log', 'GRAYLOG_PASSWORD')
    stream_id = config.get('log', 'GRAYLOG_STREAM_ID')
    fields = 'level,module,line,message,full_message,source_tag,job_id'
    params = urllib.parse.urlencode(quote_via=urllib.parse.quote, query={
        'query': f'trace_id:{job_id} and level:{level} {keyword}',
        'filter': f'streams:{stream_id}',
        'range': range,
        'limit': limit,
        'sort': 'timestamp:desc',
        'fields': fields,
    })
    url = f'http://{host}:{port}/api/search/universal/relative'
    res = requests.get(url, headers={'Accept': 'application/json'}, auth=(user, password), params=params)
    return res.json()


# logger
# config = load_config(LOG_CONFIG_FILE)
rootLogger = init_logger()
