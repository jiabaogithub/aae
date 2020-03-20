# -*- coding: utf-8 -*-
"""
本模块用于训练意图分类器
核心思想：以多项式分布为先验概率的朴素贝叶斯分类器
"""
import datetime
import logging

import jieba.analyse
from flask import current_app
from sklearn.externals import joblib
from sklearn.naive_bayes import MultinomialNB

from kbqa_sf.train.corpus.corpus_builder import build_corpus_vocabulary, cut_corpus_vocabulary
from path_configer import get_resources_trained_models, get_resources, get_resources_corpus, \
    get_classifier_train_samples

__author__ = '程序员涤生'

import codecs
import os

import jieba
import numpy as np


# 构造训练样本集
def load_train_data():
    starttime = datetime.datetime.now()
    print("构造样本集...")
    root_dir = get_classifier_train_samples()
    val_label_list = []
    for lists in os.listdir(root_dir):
        path = os.path.join(root_dir, lists)
        label = lists[:lists.find('-')]
        with codecs.open(path, "r", encoding="utf-8") as f:
            line = f.readline()
            line = line.strip("\n\r")
            while line != "":
                if line.startswith("Q "):  # 仅提取问题做为训练集
                    val_label_list.append((line, label))
                # val_label_list.append((line, label))
                line = f.readline()
                line = line.strip("\n\r")
    # 洗牌，以便均衡训练集
    print("shuffle特征集...")
    import random
    random.shuffle(val_label_list)
    features_list = []
    labels_list = []
    inb = IntentClassifierNB()
    w_i_dict = inb.load_word_index()
    for sentence, label in val_label_list:
        features_list.append(inb.build_feature(sentence, w_i_dict))
        labels_list.append(label)
    endtime = datetime.datetime.now()
    print("===========构造训练样本集耗时: %s" % (endtime - starttime).seconds)
    # 存储类别标签集合
    dump_labels_set(sorted(set(labels_list)))
    # return np.array(features_list), np.array(labels_list)
    return features_list, labels_list


class IntentClassifierNB:

    def train_clf(self):
        """
        训练分类器，并存储为文件，以便下次使用
        :return:
        """
        dump_path = "%s/classifier_mnb.m" % get_resources_trained_models()
        # 加载训练样本数据
        features_np, labels_np = load_train_data()
        features_np = np.array(features_np)
        labels_np = np.array(labels_np)
        # 开始训练
        starttime = datetime.datetime.now()
        print("开始训练分类器...")
        # 使用多项式朴素贝叶斯算法训练模型
        clf = MultinomialNB(alpha=0.1, fit_prior=True, class_prior=None)
        # 从第10个开始纳入训练，前10将做为验证集评估模型的表现
        clf.fit(features_np[10:], labels_np[10:])
        endtime = datetime.datetime.now()
        print("===========训练耗时: %s" % (endtime - starttime).seconds)
        # 评估分类器在验证集上的表现
        print("评估结果：%s" % clf.score(features_np[:10], labels_np[:10]))
        self.clf_nb = clf
        # 存储分类器
        dump_clf(self)
        print("分类器存储位置：%s" % dump_path)
        return self

    def predict(self, feature_vec, clf):
        """
        预测(基于贝叶斯模型)
        :param feature_vec: 输入句子的特征向量
        :param clf: 训练好的贝叶斯模型
        :return:
        """
        proba_pred_np = clf.clf_nb.predict_proba(np.array([feature_vec]))[0]
        logging.debug("预测结果的概率：%s", proba_pred_np)
        # 加载类别集合
        labels_set = load_labels_set()
        label_score_list = []
        for i, num in enumerate(proba_pred_np):
            # if num != 0.00000000e+00:
            if num >= current_app.config['THRESHOLD_INTENT_RECOGNITION']:
                label_score_list.append((labels_set[i], num))
        if len(label_score_list) == 0:  # 正常阈值下没有匹配项，就降级匹配
            logging.debug("意图识别在正常分数阈值下没有匹配到任何项，进行降级匹配...")
            for i, num in enumerate(proba_pred_np):
                # if num != 0.00000000e+00:
                if num >= current_app.config['MINIMUM_THRESHOLD_INTENT_RECOGNITION']:
                    label_score_list.append((labels_set[i], num))
        rs = sorted(label_score_list, key=lambda item: item[1], reverse=True)
        return rs, [c for c, v in rs]

    def build_feature(self, sentence, w_i_dict):
        """
        根据词汇表构造句子的词向量特征
        :param sentence: 句子
        :param w_i_dict: 词汇-位置索引字典
        :return: one-hot 向量
        """
        # 分词
        sentence_seg = jieba.cut(sentence)
        # 用0初始化one-hot向量，维数为词汇表的词的个数
        sen_vec = np.zeros(len(w_i_dict))
        # 词汇表的词的列表
        w_i_dict_keys = w_i_dict.keys()
        # one-hot向量对应词在词典中的位置至1
        for word in sentence_seg:
            if w_i_dict_keys.__contains__(word):
                sen_vec[w_i_dict[word]] = 1
        return sen_vec

    # 加载分类器
    def load_clf(self):
        logging.info("加载MultinomialNB分类器模型...")
        clf = load("%s/classifier_mnb.m" % get_resources_trained_models())
        logging.info("MultinomialNB分类器模型加载完成！")
        return clf

    # 完整的重新训练分类器
    def full_retrain_clf(self):
        # 构建训练语料库
        build_corpus_vocabulary()
        # 训练语料库分词
        cut_corpus_vocabulary()
        # 构建训练语料库词汇反向索引
        word_index_dict_ = load_vocabulary()
        # 存储训练语料库词汇反向索引
        dump_word_index(word_index_dict_)
        # 基于训练语料库来训练分类器模型
        self.train_clf()

    # 加载词汇反向索引
    def load_word_index(self):
        logging.info("加载词汇反向索引...")
        wi = load("%s/word.index" % get_resources())
        logging.info("词汇反向索引加载完成！")
        return wi


# 存储词汇反向索引
def dump_word_index(word_index_dict):
    return dump(word_index_dict, "%s/word.index" % get_resources())


# 加载类别标签集合
def load_labels_set():
    logging.info("加载类别标签集合...")
    lab_set = load("%s/labels_set.label" % get_resources())
    logging.info("类别标签集合加载完成！")
    return lab_set


# 存储类别标签集合
def dump_labels_set(labels_list):
    return dump(sorted(set(labels_list)), "%s/labels_set.label" % get_resources())


# 存储分类器
def dump_clf(clf):
    return dump(clf, "%s/classifier_mnb.m" % get_resources_trained_models())


# 存储
def dump(obj, dump_path):
    return joblib.dump(obj, dump_path)


# 加载
def load(obj_path):
    return joblib.load(obj_path)


# 加载词汇表
def load_vocabulary():
    vocabulary_path = "%s/question_seg.txt" % get_resources_corpus()
    logging.info("加载词汇表...")
    word_index_dict = {}
    with codecs.open(vocabulary_path, "r", encoding="utf-8") as f:
        word = f.readline()
        i = 0
        while word != "":
            word = word.strip("\n\r")
            word_index_dict[word] = i
            word = f.readline()
            i += 1
    logging.info("词汇表加载完成！")
    return word_index_dict


if __name__ == '__main__':
    pass
