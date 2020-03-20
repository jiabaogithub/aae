# -*- coding: utf-8 -*-

"""
本模块是Flask的配置模块
"""
import os

__author__ = '程序员涤生'

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:  # 基本配置类
    # SECRET_KEY = os.getenv('SECRET_KEY', b'\xe4r\x04\xb5\xb2\x00\xf1\xadf\xa3\xf3V\x03\xc5\x9f\x82$^\xa25O\xf0R\xda')
    SECRET_KEY = b'\xe4r\x04\xb5\xb2\x00\xf1\xadf\xa3\xf3V\x03\xc5\x9f\x82$^\xa25O\xf0R\xda'
    JSONIFY_MIMETYPE = 'application/json; charset=utf-8'  # 默认JSONIFY_MIMETYPE的配置是不带'; charset=utf-8的'
    JSON_AS_ASCII = False  # 若不关闭，使用JSONIFY返回json时中文会显示为Unicode字符
    ENCODING = 'utf-8'

    # 自定义的配置项
    DEFAULT_ANSWER = '额,什么意思，我没明白😓'  # 无法给出答案时的默认回复
    THRESHOLD_INTENT_RECOGNITION = 0.4  # 意图分类器的分数阈值，大于这个分数的类别才会被匹配到
    MINIMUM_THRESHOLD_INTENT_RECOGNITION = 0.1  # 意图分类器的最小分数阈值，当最大阈值没有任何匹配时，系统会自动降级到最小阈值
    THRESHOLD_SEMANTICS_UNDERSTANDER = 0.4  # 语义理解算法的分数阈值，大于这个分数的问题才会被匹配到
    MINIMUM_THRESHOLD_SEMANTICS_UNDERSTANDER = 0.09  # 语义理解算法的最小分数阈值，当最大阈值没有任何匹配时，系统会自动降级到最小阈值
    THRESHOLD_SEMANTICS_UNDERSTANDER_TALK = 0.9  # 闲聊意图-语义理解算法的分数阈值，大于这个分数的问题才会被匹配到
    THRESHOLD_SEMANTICS_UNDERSTANDER_TALK_MIN = 0.5  # 降级阈值，闲聊意图-语义理解算法的分数阈值，大于这个分数的问题才会被匹配到


class DevelopmentConfig(BaseConfig):
    ENV = 'development'
    DEBUG = True
    QUESTION_PATH = 'question_dev'
    # database配置
    USER_NAME = 'xxx'
    PWD = 'xxx'
    DATABASE_HOST = 'xx.xx.xx.xx'
    PORT = 'xx'
    DATABASE = 'xxx'
    REPLICA_SET = 'replica'
    DATABASE_URI = 'mongodb://%s:%s@%s:%s/?authSource=%s&replicaSet=%s' % (
        USER_NAME, PWD, DATABASE_HOST, PORT, DATABASE, REPLICA_SET)


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    QUESTION_PATH = 'question_dev'
    # database配置
    USER_NAME = 'xxx'
    PWD = 'xxx'
    DATABASE_HOST = 'xx.xx.xx.xx'
    PORT = 'xx'
    DATABASE = 'xxx'
    REPLICA_SET = 'replica'
    DATABASE_URI = 'mongodb://%s:%s@%s:%s/?authSource=%s&replicaSet=%s' % (
        USER_NAME, PWD, DATABASE_HOST, PORT, DATABASE, REPLICA_SET)


class ProductionConfig(BaseConfig):
    DEBUG = False
    QUESTION_PATH = 'question'
    # database配置
    USER_NAME = 'xxx'
    PWD = 'xxx'
    DATABASE_HOST = 'xx.xx.xx.xx'
    PORT = 'xx'
    DATABASE = 'xxx'
    REPLICA_SET = 'replica'
    DATABASE_URI = 'mongodb://%s:%s@%s:%s/?authSource=%s&replicaSet=%s' % (
        USER_NAME, PWD, DATABASE_HOST, PORT, DATABASE, REPLICA_SET)


config = {
    'testing': TestingConfig,
    'default': DevelopmentConfig
    # 'default': ProductionConfig
}
