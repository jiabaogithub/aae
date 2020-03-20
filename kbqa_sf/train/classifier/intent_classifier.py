# -*- coding: utf-8 -*-
"""
本模块用于训练意图分类器
核心思想：以多项式分布为先验概率的朴素贝叶斯分类器
"""
import codecs
import logging
import os

from sklearn.externals import joblib

import path_configer
from kbqa_sf.kbqa.some_decorators import singleton
from kbqa_sf.train.classifier.intent_classifier_NB import IntentClassifierNB
from kbqa_sf.train.classifier.intent_classifier_centre_vec import CentroidsVecClassifier

__author__ = '程序员涤生'


@singleton
class IntentClassifier:

    def __init__(self):
        # self.clazz = CentroidsVecClassifier()  # 选用中心向量分类器，暂时不建议使用，因为没有合适的词向量模型
        self.clazz = IntentClassifierNB()  # 选用朴素贝叶斯分类器

    # 训练分类器
    def train_clf(self):
        return self.clazz.train_clf()

    # 预测意图类别
    def predict(self, feature_vec, clf):
        return self.clazz.predict(feature_vec, clf)

    # 构造特征
    def build_feature(self, sentence, w_i_dict):
        return self.clazz.build_feature(sentence, w_i_dict)

    # 加载分类器
    def load_clf(self):
        return self.clazz.load_clf()

    # 加载词汇索引
    def load_word_index(self):
        return self.clazz.load_word_index()

    # 完整的重新训练分类器模型
    def full_retrain_clf(self):
        return self.clazz.full_retrain_clf()

    # 加载文本-向量索引
    def load_text_vec_indx(self):
        logging.info("加载文本-向量索引文件...")
        obj_path = "%s/text_vec.index" % path_configer.get_resources()
        if os.path.exists(obj_path):
            self.text_vec_indx = joblib.load(obj_path)
            logging.info("加载文本-向量索引文件完成！")
        else:
            logging.warning("未发现文本-向量索引文件！路径；%s" % obj_path)

    # 构建文本-向量索引文件，并存储
    def build_text_vec_indx(self):
        text_vec_indx = {}
        data_root_dir = path_configer.get_classifier_train_samples()
        for file in os.listdir(data_root_dir):
            vocabulary_path = os.path.join(data_root_dir, file)
            logging.info("构建文本-向量索引文件...")
            with codecs.open(vocabulary_path, "r", encoding="utf-8") as f:
                line = f.readline()
                line = line.strip("\n\r")
                while line != "":
                    if line.startswith('Q '):
                        text_vec_indx[line] = CentroidsVecClassifier().sum_vecs_avg(line)
                    line = f.readline()
                    line = line.strip("\n\r")
        logging.info("文本-向量索引文件构建完成！")
        logging.info("存储文本-向量索引文件...")
        text_vec_path = "%s/text_vec.index" % path_configer.get_resources()
        if os.path.exists(text_vec_path):
            os.remove(text_vec_path)
        joblib.dump(text_vec_indx,text_vec_path)
        logging.info("存储文本-向量索引文件完成！")
        return text_vec_indx


if __name__ == '__main__':
    pass
