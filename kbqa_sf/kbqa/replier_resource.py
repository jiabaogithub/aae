# -*- coding: utf-8 -*-

"""
问答API
"""
import logging

from kbqa_sf.kbqa.semantics.semantics_understander import get_reply

__author__ = '程序员涤生'

from flask import Blueprint, make_response, request
from flask import jsonify

replier = Blueprint('replier', __name__)

w_i_dict = None
clf_ = None


@replier.route('/ask', methods=['POST'])
def ask():
    params = request.get_json()
    if 'q' not in params or params['q'] is None or len(params['q']) > 100:
        return make_response(jsonify({'error': '问题长度不符合要求,长度限制：1~100'}), 400)
    q = "Q %s" % params['q']
    # q = params['q']
    # 构造问题特征
    question_feature = clf_.build_feature(q, w_i_dict)
    # 意图预测
    y_score_pred, y_pred = clf_.predict(question_feature, clf_)
    logging.debug("=======以下为可能的类别：")
    logging.debug(y_score_pred)
    logging.debug(y_pred)
    # 语义理解
    semantics_top_n = params['n'] if 'n' in params else None
    if semantics_top_n:
        reply_content = get_reply(y_pred, q, semantics_top_n=semantics_top_n)
    else:
        reply_content = get_reply(y_pred, q)
    return jsonify(reply_content)


if __name__ == '__main__':
    pass
