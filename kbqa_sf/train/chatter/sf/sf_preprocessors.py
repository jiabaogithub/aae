# -*- coding: utf-8 -*-

"""
扩展chatterbot的preprocessors
预先计算好问句向量，以提高性能
"""

from kbqa_sf.train.classifier.intent_classifier_centre_vec import CentroidsVecClassifier

__author__ = '程序员涤生'

def sum_vecs_avg(chatbot, statement):
    # statement_text = str(statement.text.lower())
    statement.text_vector = CentroidsVecClassifier().sum_vecs_avg(statement.text)
    return statement


if __name__ == '__main__':
    pass
