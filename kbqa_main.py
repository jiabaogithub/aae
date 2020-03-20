# -*- coding: utf-8 -*-

"""
flask 入口
"""
import kbqa_config as kc
from kbqa_sf.kbqa.flaskr import create_app, loadProjContext

__author__ = '程序员涤生'

from flask import jsonify, make_response, redirect

# 加载flask配置信息
# app = create_app('config.DevelopmentConfig')
app = create_app(kc.config['default'])
# 加载项目上下文信息
loadProjContext()

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def index_sf():
    # return render_template('index.html')
    return redirect('index.html')


if __name__ == '__main__':
    # app.run('192.168.1.107', 5002, app, use_reloader=False)
    app.run('localhost', 5002, app, use_reloader=False)




    # from werkzeug.serving import run_simple
    #
    #
    # class FixScriptName(object):
    #     def __init__(self, app):
    #         self.app = app
    #
    #     def __call__(self, environ, start_response):
    #         SCRIPT_NAME = '/kbqa_sf'
    #
    #         if environ['PATH_INFO'].startswith(SCRIPT_NAME):
    #             environ['PATH_INFO'] = environ['PATH_INFO'][len(SCRIPT_NAME):]
    #             environ['SCRIPT_NAME'] = SCRIPT_NAME
    #             return self.app(environ, start_response)
    #         else:
    #             start_response('404', [('Content-Type', 'text/plain; charset=utf-8')])
    #             # return ["This doesn't get served by your FixScriptName middleware.".encode()]
    #             return ["404.您访问的地址不存在.".encode()]
    #
    #
    # app = FixScriptName(app)
    #
    # # run_simple('localhost', 5002, app, use_reloader=False)
    # run_simple('192.168.1.107', 5002, app, use_reloader=False)
