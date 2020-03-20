# -*- coding: utf-8 -*-

"""
闲聊训练模块
"""
import codecs
import datetime
import logging

from chatterbot.comparisons import levenshtein_distance
from flask import current_app

from kbqa_sf.kbqa.some_decorators import singleton
from kbqa_sf.train.chatter.sf.sf_comparisons import WordVecComparator
from path_configer import get_chatter_corpus

__author__ = '程序员涤生'

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer


@singleton
class Talk(object):
    def __init__(self):
        logging.info('预加载Talk所有实例...')
        label = "QA_talk"
        bot_name = current_app.config['DATABASE']
        self.chat = ChatBot(
            bot_name,
            database=bot_name,
            database_uri=current_app.config['DATABASE_URI'],
            # 使用合适的词向量模型时开启
            preprocessors=[
                'kbqa_sf.train.chatter.sf.sf_preprocessors.sum_vecs_avg'
            ],
            statement_comparison_function=WordVecComparator(),
            # statement_comparison_function=levenshtein_distance,
            logic_adapters=[{'import_path': 'kbqa_sf.train.chatter.custom.custom_adapter.BestMatchExtLogicAdapter'}],
            storage_adapter="kbqa_sf.train.chatter.custom.custom_mongo_storage.MongoDatabaseExtAdapter",
            ext_collection_name=label,
            read_only=True)
        logging.info('Talk所有实例预加载完成！')


def get_chatter_bot_name():
    return "QA_talk"


def train_custom_chatbot():
    corpus_path = '%s/QA_talk-闲聊.txt' % get_chatter_corpus()
    print("开始训练...")
    starttime = datetime.datetime.now()
    chatbot = Talk().chat
    chatbot.set_trainer(ListTrainer)
    chatbot.train(read_custom(corpus_path))
    print("训练完成！")
    endtime = datetime.datetime.now()
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
            line = f.readline()
            line = line.strip("\n\r")
    print("读取完成！")
    return smaple_list


if __name__ == '__main__':
    pass
