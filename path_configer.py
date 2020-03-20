# -*- coding: utf-8 -*-

"""
本模块用于配置各文件的绝对路径
"""
import os

from flask import current_app

__author__ = '程序员涤生'


def print_proj_root():
    # print(os.path.abspath(__file__))
    # print(os.path.dirname(os.path.abspath(__file__)))
    print(os.path.abspath(os.path.dirname(__file__)))


def get_proj_root():
    return os.path.abspath(os.path.dirname(__file__))


def get_resources():
    return '%s/resources' % get_proj_root()


def get_chatter_corpus():
    return '%s/original_corpus/%s' % (get_resources(), current_app.config['QUESTION_PATH'])


def get_classifier_train_samples():
    return get_chatter_corpus()


def get_resources_custom_tokenize():
    return '%s/custom_tokenize' % get_resources()


def get_learn():
    return '%s/learn' % get_resources()


def get_resources_trained_models():
    return '%s/trained_models' % get_resources()


def get_resources_corpus():
    return '%s/corpus' % get_resources()


if __name__ == '__main__':
    print_proj_root()
