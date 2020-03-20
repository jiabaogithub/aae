# -*- coding: utf-8 -*-

"""
flask初始化
"""
from logging.config import dictConfig

from flask import Flask
from flask_cors import CORS

from kbqa_sf.kbqa import replier_resource
from kbqa_sf.kbqa.learn_resource import qac
from kbqa_sf.kbqa.replier_resource import replier
from kbqa_sf.kbqa.services_resource import services
from kbqa_sf.sentence_processer import SentenceProcesser
from kbqa_sf.train.chatter.custom.custom_chatbot import Talk
from kbqa_sf.train.chatter.sf.sf import SF
from kbqa_sf.train.classifier.intent_classifier import IntentClassifier

__author__ = '程序员涤生'


def create_app(config_type):
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(name)s %(levelname)s in %(module)s %(lineno)d: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'DEBUG',
            # 'level': 'WARN',
            # 'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
    # 加载flask配置信息
    app = Flask(__name__, static_folder='static', static_url_path='')
    # CORS(app, resources=r'/*',origins=['192.168.1.104'])  # r'/*' 是通配符，让本服务器所有的URL 都允许跨域请求
    CORS(app, resources={r"/*": {"origins": '*'}})  # r'/*' 是通配符，让本服务器所有的URL 都允许跨域请求
    app.config.from_object(config_type)
    app.register_blueprint(replier, url_prefix='/replier')
    app.register_blueprint(qac, url_prefix='/qac')
    app.register_blueprint(services, url_prefix='/services')

    # 初始化上下文
    ctx = app.app_context()
    ctx.push()

    return app


def loadProjContext():
    # 加载自定义分词表
    SentenceProcesser()
    # 加载意图分类器实例
    intent_classifier = IntentClassifier()
    # 加载词汇反向索引
    replier_resource.w_i_dict = intent_classifier.load_word_index()
    # 加载分类器模型
    replier_resource.clf_ = intent_classifier.load_clf()
    # 预加载sf所有实例
    SF()
    # 预加载talk所有实例
    Talk()
    # 加载文本向量索引文件
    IntentClassifier().load_text_vec_indx()
