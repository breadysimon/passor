from behave import *

use_step_matcher("re")


@given("我有效的用户名和手机号")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@step("我申请了验证码")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@when("我等待60秒")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@step("我使用旧的验证码进行登录")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@then("界面提示出错")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass