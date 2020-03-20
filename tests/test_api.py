import logging

import pytest

from passor import config
from passor.logging import rootLogger

logger = rootLogger.getChild(__name__)
logger.setLevel(logging.DEBUG)


class ExampleApi():
    pass


@pytest.fixture
def api() -> ExampleApi:
    config.set_env('sit')
    api0 = ExampleApi()
    yield api0
