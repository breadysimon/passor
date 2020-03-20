import logging
import urllib
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler
from urllib.parse import urlencode
from pygelf import GelfTcpHandler
import os
import requests

LOG_CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'etc', 'passart.ini')
LOG_FORMAT = '%(asctime)s [{job_id}] %(name)s %(levelname)-8s %(lineno)-2d  %(message)s'


class GELFLevel:
    DEBUG = 7
    INFO = 6
    WARNING = 4
    ERROR = 3
    CRITICAL = 2


def load_config(filename):
    cf = ConfigParser()
    data = cf.read(filename)
    if len(data) == 0:
        raise ValueError(f'加载配置文件失败,filename={filename}')

    if os.environ.get('DEBUG', default='').upper() == 'TRUE':
        cf.set('log', 'DEBUG', 'True')

    cf.add_section('runtime')

    return cf


def init_logger(name=None):
    job_id = int(config.get('runtime', 'JOB_ID'))
    logger = logging.getLogger(name)

    # TODO: log level
    logger.setLevel(logging.DEBUG)


    if 3 > len(logger.handlers):
        formatter = logging.Formatter(LOG_FORMAT.format(job_id=job_id))

        # Standard handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # File handler
        log_file = config.get('log', 'LOG_FILE').format(job_id=job_id)
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handler_file = RotatingFileHandler(filename=log_file, maxBytes=10 * 1024 * 1024, backupCount=7)
        handler_file.setFormatter(formatter)
        logger.addHandler(handler_file)

        # Graylog handler
        logger.addHandler(GelfTcpHandler(host=config.get('log', 'GRAYLOG_SERVER'),
                                         debug=True,
                                         port=config.get('log', 'GRAYLOG_TCP_PORT'),
                                         trace_id=job_id,
                                         source_tag='passart',
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
config = load_config(LOG_CONFIG_FILE)
rootLogger = init_logger()
