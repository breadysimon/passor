from collections import namedtuple


class GoldenFile:
    """Record the correct running results in a file for comparing with following test results."""

    def __init__(self, filename):
        self.filename = filename

    def make(self, text):
        with open(self.filename, 'w+') as f:
            f.write(text)

    def read(self):
        with open(self.filename) as f:
            s = f.read()
        return s


def namedlist(names, *args):
    """
    将一个无命名的元组列表转为一个有命名的元组列表,作为一个生成器提供数据。
    用法示例：
        for t in namedlist('name password',
                       ('user1', '111111'),
                       ('user2', '111111')):
            assert login(t.name, t.password)

    :param names: 用空格分开的元组字段名列表，如"field1 field2 field3"
    :param args: 每个参数是一个元组，如(1,2,3)
    :return: 一个迭代器
    """
    T = namedtuple('T', names)
    for x in args:
        yield T(*x)
