from behave import *


@given("我的帐户余额为{amount}元")
def step_impl(context, amount):
    """
    :type context: behave.runner.Context
    """
    pass


@step("我有有效的银行卡")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@step("提款机有足够现金")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@when("我要求取款{amount}元")
def step_impl(context, amount):
    """
    :type context: behave.runner.Context
    """
    pass


@then("提款机吐{amount}元")
def step_impl(context, amount):
    """
    :type context: behave.runner.Context
    """
    pass


@step("提款机应该退还银行卡")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@step("我的帐户余额为{amount:d}元")
def step_impl(context, amount):
    """
    :type context: behave.runner.Context
    """
    pass


@then("提款机提示'{message}'")
def step_impl(context, message):
    """
    :type context: behave.runner.Context
    """
    assert '非法请求' == message
    pass
