# -*- coding: utf-8 -*-

"""
本模块用于加载训练好的模型
"""
import logging

from kbqa_sf.kbqa.some_decorators import singleton
from path_configer import get_resources_trained_models

__author__ = '程序员涤生'

from gensim import models


def get_prefix_path():
    return get_resources_trained_models()


@singleton
class ModelsLoader():
    def __init__(self):
        self.sf_words_vec_model = self.__load_sf_words_vec_model()

    # 加载训练好的SF词向量模型
    def __load_sf_words_vec_model(self):
        logging.info("加载SF词向量模型...")
        model = models.KeyedVectors.load("%s/sgns.zhihu.bigram-char.model" % get_prefix_path(), mmap='r')
        model.wv.vectors_norm = model.wv.vectors
        logging.info("SF词向量模型加载完成！")
        return model


def get_classifier_path():
    return "%s/classifier.m" % get_prefix_path()


if __name__ == '__main__':
    pass
