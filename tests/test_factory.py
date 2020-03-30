import os

from hamcrest import *

from passor import util
from passor.apiclient import ServiceCallerFactory
from passor.config import set_env


def test_get_caller():
    set_env('sit')
    af = ServiceCallerFactory(util.get_relative_path(__file__, "examples"))
    a = af.get_caller('example')

    assert_that(a.name, equal_to('example'))
    assert_that(a.root_uri, equal_to('https://sit-site/'))

