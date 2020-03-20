# -*- coding: utf-8 -*-

"""
qac学习API
包括：更新已有答案、标注正确答案、添加新问题和答案
qac_list_str = '''
[
    {"q": "q_QA_sf_exchange_rate_1", "a": "a_QA_sf_exchange_rate_1", "c": "QA_sf_exchange_rate"},
    {"q": "q_talk_1", "a": "a_talk_1", "c": "QA_talk"}
]
'''
q:问题;a:答案;c:业务类别，比如QA_sf_exchange_rate-汇率、QA_sf_export_write_downs-出口冲减等
"""
import codecs
import logging
import os
import threading
import time
import datetime

from chatterbot.conversation import Statement

import path_configer
from kbqa_sf.train.chatter.custom.custom_chatbot import train_custom_chatbot, Talk
from kbqa_sf.train.chatter.sf.sf import train_sf_chatbot, SF
from kbqa_sf.train.classifier.intent_classifier import IntentClassifier

__author__ = '程序员涤生'

from flask import Blueprint, request, jsonify, make_response

qac = Blueprint('qac', __name__)

__record_lock = threading.Lock()


@qac.route('/all_classify', methods=['GET'])
def load_all_classify():
    file_names = [
        {
            "code": file_name[:file_name.find("-")],
            "text": file_name[file_name.find("-") + 1:file_name.find(".")]
        } for file_name in os.listdir(path_configer.get_chatter_corpus())]
    logging.debug("所有的类别包括：%s", file_names)
    return jsonify(file_names)


@qac.route('/record', methods=['POST'])
def record():
    """
    将要学习的问题、答案、类别，写入文件learn目录下的wait-learn.txt、history-learn.txt
    :return:
    """
    qac_list = request.get_json()
    learn_path = path_configer.get_learn()
    wait_learn_path = "%s/%s" % (learn_path, "wait-learn.txt")
    history_learn_path = "%s/%s" % (learn_path, "history-learn.txt")
    with __record_lock:
        fa_wait = codecs.open(wait_learn_path, "a", encoding="utf-8")
        fa_history = codecs.open(history_learn_path, "a", encoding="utf-8")
        for qac_item in qac_list:
            q = qac_item["q"]
            a = qac_item["a"]
            c = qac_item["c"]
            if 0 < len(a) <= 300 and len(q) > 0 and len(c) > 0:
                content = 'Q %s\nA %s\nC %s\n' % (q, a, c)
                fa_wait.write(content)
                fa_history.write(
                    '%sT %s\n' % (content, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            else:
                return make_response(jsonify({'error': '参数不符合要求，请检查！'}), 400)
        fa_wait.close()
        fa_history.close()
        logging.debug("=========待学习问题记录完成！")
    return "success"


@qac.route('/learn/batch', methods=['GET'])
def learn_batch():
    """
    批量学习给定的问题和答案:
    重命名wait-learn.txt为learning.txt,读取learning.txt的内容进行学习
    :return:
    """
    _learn_new_batch_lock = threading.Lock()
    logging.debug("开始学习...")
    starttime = datetime.datetime.now()
    learn_path = path_configer.get_learn()
    wait_learn_path = "%s/%s" % (learn_path, "wait-learn.txt")
    learning_path = "%s/%s" % (learn_path, "learning.txt")
    with __record_lock:
        if os.path.exists(learning_path):
            # 若上一次的临时文件未能删除，就在这里删除。
            os.remove(learning_path)
            logging.info("=========发现上一次的临时文件未能删除，已删除！")
        if not os.path.exists(wait_learn_path):
            msg = "nothing"
            logging.info(msg)
            return msg
        os.rename(wait_learn_path, learning_path)
        logging.debug("重命名wait-learn.txt为learning.txt ...")
    with _learn_new_batch_lock:
        logging.debug("读取learning.txt的内容进行学习 ...")
        with codecs.open(learning_path, "r", encoding="utf-8") as fr:
            q = fr.readline().strip("\n\r")
            while q != "":
                a = fr.readline().strip("\n\r")
                assert a.strip("\n\r") != "", 'q,a,c格式无法匹配！缺少a！'
                c = fr.readline().strip("\n\r")
                assert c.strip("\n\r") != "", 'q,a,c格式无法匹配！缺少a！'
                # 添加q,a到指定的c类别文件；训练c对应的chatterbot
                logging.debug("添加%s,%s到指定的%s类别文件；训练对应的chatterbot ...", q, a, c)
                # 开始学习
                learn_(q, a, c[c.find(" ") + 1:])
                q = fr.readline().strip("\n\r")
        logging.debug("learning.txt学习全部完成...")
        logging.debug("完整的重新训练分类器模型 ...")
        IntentClassifier().full_retrain_clf()
        logging.debug("构建文本-向量索引文件，并存储 ...")
        IntentClassifier().build_text_vec_indx()
        logging.debug("加载文本向量索引文件 ...")
        IntentClassifier().load_text_vec_indx()
        # 删除临时的学习文件
        os.remove(learning_path)
        endtime = datetime.datetime.now()
        print("===========本次学习耗时: %s秒" % (endtime - starttime).seconds)
        logging.info("=========本次学习已全部完成！")
    return "success"


@qac.route('/reset', methods=['GET'])
def reset():
    logging.debug("重新训练业务专业领域问答机器人...")
    train_sf_chatbot()
    logging.debug("重新训练闲聊机器人 ...")
    train_custom_chatbot()
    logging.debug("完整的重新训练分类器模型 ...")
    IntentClassifier().full_retrain_clf()
    return "success"


def learn_(q, a, c):
    """
    添加q,a到指定的c类别文件；训练c对应的chatterbot
    :param q: 问题
    :param a: 答案
    :param c: 分类
    :return:
    """
    file_names = [file_name for file_name in os.listdir(path_configer.get_chatter_corpus()) if
                  file_name.startswith(c)]
    if not file_names:
        logging.warning("未知的类别：%s,已忽略", c)
        return
    file_name = file_names[0]
    file_path = "%s/%s" % (path_configer.get_chatter_corpus(), file_name)
    # 追加到c对应的意图分类文件中
    with codecs.open(file_path, "a", encoding="utf-8") as fa:
        if len(q) > 0 and len(a) > 0:
            if os.path.getsize(file_path) == 0:
                fa.write('%s' % q)
            else:
                fa.write('\n%s' % q)
            fa.write('\n%s' % a)
    # 学习问答
    qa_learn(q, a, c)
    return "success"


def qa_learn(q, a, c):
    a_statement = Statement(a)
    q_statement = Statement(q)
    if c.startswith("QA_talk"):
        chat_bot = Talk().chat
    else:
        chat_bot = SF().chatters[c]
    chat_bot.learn_response(a_statement, q_statement)


if __name__ == '__main__':
    pass
    # record()
    # learn_batch()
    # load_all_classify()
