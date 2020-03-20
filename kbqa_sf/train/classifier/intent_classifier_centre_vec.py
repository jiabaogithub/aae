# -*- coding: utf-8 -*-

"""
本模块用于训练意图分类器
"""
import logging

from flask import current_app

import path_configer
from kbqa_sf.kbqa.models_loader import ModelsLoader
from kbqa_sf.kbqa.some_decorators import singleton
from path_configer import get_resources_trained_models

__author__ = '程序员涤生'

import codecs
import os
import pickle

import jieba
import numpy as np


@singleton
class DataLoader:
    def load_train_data(self):
        """
        加载训练数据
        :return: {'类别':{examples:'句子样本',centroid:'中心向量'}}
        """
        rs = {}
        samples = self.__get_samples(path_configer.get_classifier_train_samples())
        intents_labels = samples.keys()
        for lab in intents_labels:
            labels_dict = {}
            examples_list = []
            texts = samples[lab]
            for t in texts:
                examples_list.append(t)
            labels_dict["examples"] = examples_list
            labels_dict["centroid"] = None
            rs[lab] = labels_dict
        return rs

    # 加载测试数据
    def load_test_data(self):
        samples = self.__get_samples(path_configer.get_classifier_train_samples())
        intents_labels = samples.keys()
        examples_dict = {}
        for lab in intents_labels:
            texts = samples[lab]
            for t in texts:
                examples_dict[t] = lab
        return examples_dict

    # 从文件中获取{标签:句子}格式的字典
    def __get_samples(self, data_root_dir):
        labels_texts_dict = {}
        for lists in os.listdir(data_root_dir):
            path = os.path.join(data_root_dir, lists)
            label = lists[:lists.find('-')]
            # label = lists
            texts_list = []
            with codecs.open(path, "r", encoding="utf-8-sig") as f:
                line = f.readline()
                while line != "":
                    line = line.strip("\n\r")
                    # if line.startswith("Q "):  # 仅提取问题做为训练集
                    #     texts_list.append(line)
                    texts_list.append(line)
                    line = f.readline()
            labels_texts_dict[label] = texts_list
        return labels_texts_dict


class CentroidsVecClassifier:

    def sum_vecs_avg(self, text):
        """
        根据词向量模型构建句子向量
        :param text: 句子
        :return:
        """
        # 加载词向量模型
        word_vec_model = ModelsLoader().sf_words_vec_model
        # 用0值初始化一个同维数的向量，如果你知道你的词向量模型是多少维的，可以直接指定，不用采用下面的野路子
        vec = np.zeros(word_vec_model['是'].shape[0])
        # 分词
        words_list = list(jieba.cut(text))
        for w in words_list:
            try:
                # 将所有词的向量累加
                vec = vec + word_vec_model[w]
            except KeyError as e:
                logging.warning('词‘%s’，不在词向量模型词汇表中', w)
                continue
            except ValueError as e:
                logging.error('Error:', e)
                break
        # 计算平均向量
        vec = vec / len(words_list)
        return vec

    def predict(self, feature_vec, clf):
        """
        预测意图类别
        :param feature_vec: 输入句子的特征向量
        :param clf: 从接口继承下来的参数，这里用不到
        :return:
        """
        intents = self.labels
        # 分数计算规则：计算新句子的向量和当前意图类别的中心向量的夹角余弦值，下面其实可以改进以下，用矩阵并行计算代替for循环，但是因为类别目前不多，影响暂时不大。
        scores = [(label_, np.dot(feature_vec, self.labels_centroids_dict[label_]) / (
                np.linalg.norm(feature_vec) * np.linalg.norm(self.labels_centroids_dict[label_]))) for label_ in
                  intents]
        rs = sorted(scores, key=lambda item: item[1], reverse=True)
        top1scores = rs[0][1]
        top1label = rs[0][0]
        logging.debug("top1的分数：%s,label:%s", top1scores, top1label)
        if top1scores >= current_app.config['THRESHOLD_INTENT_RECOGNITION']:
            rs = rs[:1]
        elif top1scores >= current_app.config['MINIMUM_THRESHOLD_INTENT_RECOGNITION']:
            logging.debug("意图识别在正常分数阈值下没有匹配到任何项，进行降级匹配...")
        elif top1scores < current_app.config['MINIMUM_THRESHOLD_INTENT_RECOGNITION']:
            logging.debug("意图识别在最小分数阈值下没有匹配到任何项...")
            rs = []
        return rs, [c for c, v in rs]

    # 根据词汇表构造句子的词向量特征
    def build_feature(self, sentence, w_i_dict):
        return self.sum_vecs_avg(sentence)

    def train_clf(self):
        """
        训练分类器(基于中心向量的方式)
        :return:
        """
        data = DataLoader().load_train_data()
        logging.info("开始训练...")
        _, labels_centroids_dict = self.cal_centroid_vec(data)
        self.labels_centroids_dict = labels_centroids_dict
        self.labels = list(labels_centroids_dict.keys())
        logging.info("训练完成！")
        # 存储分类器模型
        self.dump(self)
        return self

    def cal_centroid_vec(self, data):
        """
        构建“类别-中心向量”字典
        :param data: {'类别':{examples:'句子样本',centroid:'中心向量'}}
        :return:
        """
        labels_centroids_dict = {}
        for the_label in data.keys():
            centroid = self.get_centroid(data[the_label]["examples"])
            data[the_label]["centroid"] = centroid
            labels_centroids_dict[the_label] = centroid
        return data, labels_centroids_dict


    def get_centroid(self, examples):
        """
        获取当前意图类别的中心向量。中心向量由examples中所有句子向量各分量上的算数平均数表示
        :param examples: 当前类别下的所有样本句子
        :return:
        """
        word_vec_model = ModelsLoader().sf_words_vec_model
        word_dim = word_vec_model['是'].shape[0]
        C = np.zeros((len(examples), word_dim))
        for idx, text in enumerate(examples):
            C[idx, :] = self.sum_vecs_avg(text)
        centroid = np.mean(C, axis=0)
        assert centroid.shape[0] == word_dim
        return centroid

    # 评估
    def evaluate_clf(self, top_n=3):
        sentences_labels_dict = DataLoader().load_test_data()
        text_list_ = sentences_labels_dict.keys()
        correct_counts = 0
        error_list = []
        for text_ in text_list_:
            text_vec = self.build_feature(text_, None)
            s_y_pred, y_pred = self.predict(text_vec, None)
            y_pre_topn_list = y_pred[:top_n]
            y_true = sentences_labels_dict[text_]
            if y_pre_topn_list.__contains__(y_true):
                correct_counts += 1
            else:
                error_list.append(
                    "sentence:%s, y_true:%s , s_y_pred:%s "
                    % (text_, y_true, s_y_pred))
        print("测试数据总数：%s" % len(text_list_))
        print("正确预测数：%s" % correct_counts)
        print("错误预测数：%s" % (len(text_list_) - correct_counts))
        print("正确率：%s" % (correct_counts / len(text_list_)))
        print("以下是本次预测错误的句子===========>")
        [print(err) for err in error_list]

    # 存储
    def dump(self, obj):
        logging.info("开始存储分类器模型...")
        with open("%s/classifier_word2vec.m" % get_resources_trained_models(), 'wb') as f:
            pickle.dump(obj, f)
        logging.info("存储分类器模型完成！")

    # 加载
    def load_clf(self):
        logging.info("加载centre_vec分类器模型...")
        with open("%s/classifier_word2vec.m" % path_configer.get_resources_trained_models(), 'rb') as f:
            clf = pickle.load(f)
        logging.info("centre_vec分类器模型加载完成！")
        return clf

    # 完整的重新训练分类器
    def full_retrain_clf(self):
        self.train_clf()

    # 加载词汇反向索引
    def load_word_index(self):
        return None


if __name__ == '__main__':
    # 训练分类器模型
    clf_ = CentroidsVecClassifier()
    clf_ = clf_.train_clf()
    clf_path_ = "%s/classifier_word2vec.m" % get_resources_trained_models()

    # # 评估分类器模型
    # clf_ = CentroidsVecClassifier()
    # clf_ = clf_.load(clf_path_)
    # data_loader = DataLoader()
    # test_sentence_lab_dict = data_loader.load_test_data()
    # clf_.evaluate(test_sentence_lab_dict, 5)

    # # 测试分类器
    # clf_ = CentroidsVecClassifier()
    # clf_ = clf_.load(clf_path_)
    # while True:
    #     '''
    #     问题样例:
    #         周星驰演过哪些电影?
    #         阿凡达是奇幻片吗？
    #    '''
    #     # 提问
    #     question = input()
    #     # 将问题抽象处理
    #     q_abs, ne_flag_word_dict = SentenceProcesser().abstract_sentence(question)
    #     # 意图预测
    #     s_y_pred = clf_.predict_intent(q_abs, word_vec_model_)[:5]
    #     print("=======以下为可能的类别：")
    #     print(s_y_pred)
