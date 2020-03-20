# -*- coding: utf-8 -*-

"""
闲聊模块
"""
import datetime
import logging

from kbqa_sf.train.chatter.custom.custom_chatbot import Talk

__author__ = '程序员涤生'


def reply(label, chat_sentence):
    logging.debug("问题类型：闲聊")
    starttime2 = datetime.datetime.now()
    statement_obj = Talk().chat.get_response(chat_sentence)
    statement_list = statement_obj.response_closest_list
    endtime2 = datetime.datetime.now()
    logging.debug("===========chat.get_response耗时: %s秒" ,(endtime2 - starttime2).seconds)
    if not statement_list:
        return []
    else:
        # 从2开始是为了去除"number "标识符
        return [(statement.in_response_to[0].text[statement.in_response_to[0].text.find(' ') + 1:],  # 问题文本
                 statement.text[statement.text.find(' ') + 1:],  # 答案文本
                 statement.confidence,  # 得分
                 statement.in_response_to[0].text[:statement.in_response_to[0].text.find(' ')]  # 问题标签
                 ) for statement in statement_list]


if __name__ == '__main__':
    pass
