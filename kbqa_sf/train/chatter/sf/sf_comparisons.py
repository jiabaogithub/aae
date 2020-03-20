# -*- coding: utf-8 -*-

"""
扩展chatterbot的Comparator
"""

import numpy as np
from chatterbot.comparisons import Comparator

__author__ = '程序员涤生'


class WordVecComparator(Comparator):

    def compare(self, statement, statement_vec):
        """
        比较夹角余弦值
        :param statement: 输入句子对象
        :param statement_vec: 句子样本特征向量，是一个二维list
        :return: 输入句子和各句子样本的相似度构成的二维数组
        """
        statement_text_vec = statement.text_vector
        statement_vec = np.array(statement_vec)
        # 向量化并行计算余弦值
        similarity = np.dot(statement_text_vec, statement_vec.T) / (
                    np.linalg.norm(statement_text_vec) * np.linalg.norm(statement_vec, axis=1)).T
        print("similarity.shape %s" % similarity.shape)
        return similarity


if __name__ == '__main__':
    pass
