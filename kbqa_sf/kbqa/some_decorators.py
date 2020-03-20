# -*- coding: utf-8 -*-

"""
本模块包含了一些有用的装饰器，能让一些代码的设计更优雅。
比如：单例模式装饰器
"""

__author__ = '程序员涤生'


# 使用装饰器(decorator),
# 这是一种更pythonic,更elegant的方法,
# 单例类本身根本不知道自己是单例的,因为他本身(自己的代码)并不是单例的
def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


if __name__ == '__main__':
    @singleton
    class C(object):
        a = 1

        def __init__(self, x=0):
            self.x = x


    one = C()
    two = C()
    two.a = 1
    print(one.a==two.a)  # True
    print(id(one) == id(two))  # True
    print(one == two)  # True
    print(one is two)  # True
