# -*- coding: utf-8 -*-

"""
句子处理模块
"""
import logging

from kbqa_sf.kbqa.some_decorators import singleton
from path_configer import get_resources_custom_tokenize

__author__ = '程序员涤生'

import jieba
import jieba.analyse


@singleton
class SentenceProcesser:

    def __init__(self):
        logging.info("加载自定义分词表...")
        prefix_path = get_resources_custom_tokenize()
        jieba.load_userdict("%s/sf_tokenize_dict.txt" % prefix_path)
        logging.info("自定义分词表加载完成！")

    # 将句子抽象处理
    # def abstract_sentence(self, sentence):
    #     # 命名实体集合
    #     ne_dict = {"movie": "电影名", "nr": "人名", "genre": "体裁", "score": "分值"}
    #     ne_dict_keys = ne_dict.keys()
    #     # sentence_new = self.extract_keywords(sentence) #提取关键词做为新句子
    #     sentence_new = sentence  # 使用原句子
    #     word_flag_pair = pseg.cut(sentence_new)
    #     ne_flag_word_dict = {}
    #     for w in word_flag_pair:
    #         if ne_dict_keys.__contains__(w.flag):
    #             sentence_new = sentence_new.replace(w.word, w.flag)
    #             # 考虑到会有相同的命名实体词性的情况，所以用{词性:[]}格式记录这些命名实体和词性的关系，以便检索时使用
    #             if w.flag in ne_flag_word_dict:
    #                 ne_flag_word_dict[w.flag].append(w.word)
    #             else:
    #                 ne_flag_word_dict[w.flag] = [w.word]
    #     logging.debug(sentence_new)
    #     return sentence_new, ne_flag_word_dict

    # 提取关键词做为新句子
    # def extract_keywords(self, sentence):
    #     keywords_list = jieba.analyse.extract_tags(sentence, 5, withWeight=False)
    #     logging.debug(jieba.analyse.extract_tags(sentence, 5, withWeight=True))
    #     keywords = [(sentence.index(keyword), keyword) for keyword in keywords_list]
    #     keywords.sort()
    #     keywords_sorted = [keyword for index, keyword in keywords]
    #     return "".join(keywords_sorted)


if __name__ == '__main__':
    # print(os.path.abspath(__file__))
    # print(os.path.dirname(os.path.abspath(__file__)))
    # SentenceProcesser()
    pass
