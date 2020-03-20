# -*- coding: utf-8 -*-

"""
tornado 入口
"""

__author__ = '程序员涤生'

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from kbqa_main import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(4000, '192.168.1.107')
# http_server.listen(8888, '192.168.0.139')
IOLoop.instance().start()
