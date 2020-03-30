# Created by 050253 on 2018/6/15
import os
import re
import sys
from random import random

import pytest
from hamcrest import *
from hamcrest import assert_that
from retry.api import retry_call

from passor import util
from passor.config import config
from passor.logging import get_logger, init_logger, query_graylog, GELFLevel
from passor.testing import GoldenFile


@pytest.mark.parametrize('level', ['ERROR' ,'DEBUG'])
def test_generic_usage(capsys, level):
    config.set('log', 'level', level)

    l = init_logger(level.lower())
    logger = l.getChild(__name__)

    logger.error('this is an error level message.')
    logger.info('this is an info level message.')

    text = re.sub(r'-\d+-\d+\s+\d+:\d+\:\d+\,\d+', repl='-00-00 00:00:00,000', string=capsys.readouterr().err)
    text = re.sub(r':\d+:', repl=':00:', string=text)
    gf1 = GoldenFile(util.get_relative_path(__file__, 'examples', f'logging_pattern_{level}.txt'))
    # gf1.make(text)
    assert_that(text, equal_to(gf1.read()))


@pytest.mark.skipif(sys.platform != 'linux', reason='cant only test it on server side')
def test_graylog():
    logger = get_logger(__name__)

    rand = str(random())
    debug_msg = 'this is an debug level message to graylog.' + rand
    err_msg = 'this is an error level message to graylog.' + rand
    logger.error(err_msg)
    logger.debug(debug_msg)
    try:
        1 / 0
    except:
        logger.exception('some exception' + rand)

    def fetch():
        ret1 = query_graylog(job_id=0, range=300, level=GELFLevel.DEBUG, keyword=rand)
        ret2 = query_graylog(job_id=0, range=300, level=GELFLevel.ERROR, keyword=rand)

        assert_that(ret1, contains_string(debug_msg))
        assert_that(ret2, not (contains_string(debug_msg)))
        assert_that(ret2, contains_string('Traceback'))

    # it's difficult to make sure how long the delay will be. force to retry 60s.
    retry_call(fetch, tries=20, delay=3)
