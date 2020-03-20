# -*- coding: utf-8 -*-

"""
业务语料库训练模块
"""
import logging

from chatterbot.comparisons import levenshtein_distance
from flask import current_app

from kbqa_sf.kbqa.some_decorators import singleton
from kbqa_sf.train.chatter.sf.sf_comparisons import WordVecComparator

__author__ = '程序员涤生'

import codecs
from datetime import datetime
import os

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

import path_configer
from path_configer import get_chatter_corpus


@singleton
class SF(object):
    def __init__(self):
        logging.info('预加载sf词向量模型...')
        logging.info('预加载SF所有实例...')
        labels = [file_name[:file_name.find("-")] for file_name in os.listdir(path_configer.get_chatter_corpus()) if
                  file_name.startswith("QA_sf_")]
        chatters = {}
        bot_name = current_app.config['DATABASE']
        # 根据不同的类型，创建不同的ChatBot实例
        for label in labels:
            chatters[label] = (
                ChatBot(
                    bot_name,
                    database=bot_name,
                    database_uri=current_app.config['DATABASE_URI'],
                    # 使用合适的词向量模型时开启
                    preprocessors=[
                        'kbqa_sf.train.chatter.sf.sf_preprocessors.sum_vecs_avg'
                    ],
                    statement_comparison_function=WordVecComparator(),
                    # statement_comparison_function=levenshtein_distance,
                    logic_adapters=[{'import_path': 'kbqa_sf.train.chatter.sf.sf_adapter.BestMatchExtLogicAdapter'}],
                    storage_adapter="kbqa_sf.train.chatter.sf.sf_mongo_storage.MongoDatabaseExtAdapter",
                    ext_collection_name=label,
                    read_only=True)
            )
        self.chatters = chatters
        logging.info('SF所有实例预加载完成！')


def __train(corpus_path, collection_name):
    print("开始训练SF...")
    starttime = datetime.now()
    chatbot = SF().chatters[collection_name]
    chatbot.set_trainer(ListTrainer)
    chatbot.train(read_custom(corpus_path))
    print("SF训练完成！")
    endtime = datetime.now()
    print("===========训练耗时: %s秒" % (endtime - starttime).seconds)


def read_custom(corpus_path):
    smaple_list = []
    print("开始读取聊天语料库%s" % corpus_path)
    with codecs.open(corpus_path, "r", encoding="utf-8") as f:
        line = f.readline()
        line = line.strip("\n\r")
        i = 1
        while line != "":
            # smaple_list.append("%s %s" % (i, line[line.find(" "):]))
            smaple_list.append(line)
            i += 1
            # SentenceProcesser()
            # text = jieba.analyse.extract_tags(line[:], 20)
            # text.reverse()
            # smaple_list.append("".join(text))
            line = f.readline()
            line = line.strip("\n\r")
    print("读取完成！")
    return smaple_list


def train_sf_chatbot():
    data_root_dir = path_configer.get_classifier_train_samples()
    for file_name in os.listdir(data_root_dir):
        if file_name.startswith("QA_sf_"):
            __train(('%s/%s' % (get_chatter_corpus(), file_name)), file_name[:file_name.find('-')])


if __name__ == '__main__':
    chat_bot = SF().chatters['QA_sf_As_domestic_sales']
    while True:
        q = input("我：")
        response = chat_bot.get_response(q)
        print("小天：%s" % response)
