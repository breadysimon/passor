import os

from hamcrest import *

from passor import util
from passor.apiclient import ServiceCallerFactory


def test_get_caller():
    af = ServiceCallerFactory(util.get_relative_path(__file__, "examples"))
    a = af.get_caller('example', 'sit')

    assert_that(a.name, equal_to('example'))
    assert_that(a.environmental_config.apiUrlRoot, equal_to('https://sit-site/'))

