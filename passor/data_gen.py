import random
import string
from faker import Faker


def random_int(length=10):
    """
    :param length:
    :return:
    """
    return str("".join(random.choice(string.digits[1:-1]) for _ in range(length)))


funcs = [random_int]


class DataGen:

    def __init__(self):
        self.faker = Faker("zh_CN")
        # 注册自定义数据生成函数
        for f in funcs:
            setattr(self.faker, f.__name__, f)

    def gen(self, type, *args, **kwargs):
        # 未注册的方法，直接返回None
        if not hasattr(self.faker, type):
            return ''
        if args or kwargs:
            return eval(f"self.faker.{type}(*{args}, **{kwargs})")
        else:
            return eval(f"self.faker.{type}()")
