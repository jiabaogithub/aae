# -*- coding: utf-8 -*-

"""
本模块用于测试结巴分词
"""
from kbqa_sf.sentence_processer import SentenceProcesser

__author__ = '程序员涤生'

import jieba.analyse
import jieba.posseg as pseg

# sentence = "周星驰演过那些电影？"
# sentence = "卧虎藏龙的评分怎么样？"
# sentence = "阿凡达是奇幻片吗？"
# sentence = "巩俐演的评分低于6的电影"
# sentence = "你会什么"
# sentence = "该报关单已申报退运已补税未退税证明？"
# sentence = "上个月做了退运已补税未退税证明，税务局给了证明，本月做退运补税证明冲减录入后自助办税提示该报关单美元离岸价超过合理范围怎么处理？"
# sentence = "什么时候需要做出口冲减？"
sentence = "再见"

# 载入自定义的词典
SentenceProcesser()

# 精确模式，不传cut_all参数就是默认精确模式
seg_list = jieba.cut(sentence, cut_all=False)
print("/ ".join(seg_list))
# 全模式
seg_list = jieba.cut(sentence, cut_all=True)
print("/ ".join(seg_list))
# 搜索引擎模式
seg_list = jieba.cut_for_search(sentence)
print("/ ".join(seg_list))

# 关键字提取
seg_list = jieba.analyse.extract_tags(sentence, 20)
seg_list.reverse()
word_flag_pair = pseg.cut("".join(seg_list))
for w in word_flag_pair:
    print(w.word, w.flag)
