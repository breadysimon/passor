# Created by 050253 on 2018/6/15
import os
import re
import sys
from random import random

import pytest
from hamcrest import *
from hamcrest import assert_that, is_not, calling, raises
from retry.api import retry_call

from passor.logging import get_logger, init_logger, query_graylog, GELFLevel, config
from passor.testing import GoldenFile


def test_generic_usage(capsys):

    os.environ['DEBUG'] = 'TRUE'

    # have to start after capsys definition for capture log
    mock_root = init_logger('xxx')
    logger = mock_root.getChild(__name__)

    logger.error('this is an error level message.')
    logger.info('this is an info level message.')

    text = re.sub('-\d+-\d+\s+\d+:\d+\:\d+\,\d+', repl='-00-00 00:00:00,000', string=capsys.readouterr().err)
    text = re.sub(':\d+:', repl=':00:', string=text)
    gf1 = GoldenFile('resources/logging_pattern_01.txt')
    False and gf1.make(text)  # 需要更新记录文件时改为True
    assert_that(text, equal_to(gf1.read()))


@pytest.mark.skipif(sys.platform == 'darwin', reason='too slow')
def test_graylog():
    """将日志提交到Graylog,再从Graylog查询得到不同级别的日志"""

    logger = get_logger(__name__)

    rand = str(random())
    debug_msg = 'this is an debug level message to graylog.' + rand
    err_msg = 'this is an error level message to graylog.' + rand
    logger.error(err_msg)
    logger.debug(debug_msg)
    try:
        x = 1 / 0
    except:
        logger.exception('some exception' + rand)

    def fetch():
        ret1 = query_graylog(job_id=0, range=300, level=GELFLevel.DEBUG, keyword=rand)
        ret2 = query_graylog(job_id=0, range=300, level=GELFLevel.ERROR, keyword=rand)

        assert_that(ret1, contains_string(debug_msg))
        assert_that(ret2, not (contains_string(debug_msg)))
        assert_that(ret2, contains_string('Traceback'))

    # graylog的延时时长不确定，所以重试等待, 最长60s
    retry_call(fetch, tries=20, delay=3)


def test_config():
    """加载配置文件成功后读取配置"""
    assert_that(config.get('log', 'GRAYLOG_SERVER'), is_not(''))


def test_config_missing_file():
    """加载配置文件失败抛出异常"""
    assert_that(calling(load_config).with_args('non_exist'), raises(ValueError))
