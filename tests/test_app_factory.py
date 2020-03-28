import os

from hamcrest import *

from passor.apiclient import ApplicationFactory


def test_get_app():
    af = ApplicationFactory(os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples"))
    a = af.get_app('example', 'sit')
    assert_that(a.name, equal_to('example'))
    assert_that(a.environmental_config.apiUrlRoot, equal_to('https://sit-site/'))
