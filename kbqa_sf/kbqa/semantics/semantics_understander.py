# -*- coding: utf-8 -*-

"""
语义理解模块
"""
import logging
import traceback

from flask import current_app

from kbqa_sf.kbqa.semantics.q_a import question_answer, question_answer_talk

__author__ = '程序员涤生'


def get_reply(y_pred, original_question, top_n=3, semantics_top_n=3):
    """
    获取回复
    :param y_pred: ['film_genre','film_introduction',...]
    :param original_question: 原问题句子
    :param top_n: 取最可能的前n个类别,默认为3
    :return:
    从最接近的意图开始查询答案，过滤掉查不出答案的意图，若所有意图都查不到答案，则返回“这个题目太难了！~我不会做！~不会做啊！~”;
    若能查询到答案的意图数目>1 ，则将第一个意图的答案做为问题答案，其它意图和答案做为附加响应，以便用户选择;
    若能查询到答案的意图数目<1,则直接将第一个意图的答案做为问题答案，不做附加响应;
    若最匹配的意图是闲聊，就直接交给闲聊引擎处理。
    """
    if not y_pred:
        logging.warning('未能匹配到任何意图类别！')
        return build_content([])
    # 获取标准答案和候选问答
    y_pred = y_pred[:top_n]
    logging.debug("预测类别top%s：%s", top_n, y_pred)
    rs_list = []
    # 一问一答：闲聊 只有闲聊概率最大的时候才被匹配,并且匹配后直接返回
    for i, label in enumerate(y_pred):
        try:
            if label.startswith('QA_talk') and i == 0 or len(original_question)==1:
                logging.debug("策略：一问一答-闲聊；类别：%s", label)
                q_a_rs_list = question_answer_talk.reply(label, original_question)
                if q_a_rs_list:
                    rs_list = [q_a_rs_list[0]]  # 只要匹配到了闲聊，就只返回闲聊匹配度最高的回复
                # 构造回复内容
                reply_content = build_content(rs_list)
                reply_content["c"] = label
                return reply_content
            else:
                break
        except Exception as e:
            logging.error(e)
            traceback.print_exc()

    # 一问一答：业务专业知识
    for i, label in enumerate(y_pred):
        try:
            if label.startswith('QA_talk'):  # 一问一答：闲聊 直接跳过
                continue
            elif label.startswith('QA_sf_'):
                logging.debug("策略：一问一答-专业知识；类别：%s", label)
                q_a_rs_list = question_answer.reply(label, original_question)
                if q_a_rs_list:
                    rs_list.extend(q_a_rs_list)
            else:
                logging.warning("发现错误的命名规则：%s, 既不是以QA_talk也不是以QA_sf_开头", label)
                continue
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            continue
    # 构造回复内容
    if len(rs_list) == 0:
        reply_content = build_qa_specialty_content(rs_list)
    elif rs_list[0][2] > 0.95: # 若第一条问答对的分数大于某个阈值，则只返回该条问答对
        reply_content = build_qa_specialty_content(rs_list[:1])
    else:
        reply_content = build_qa_specialty_content(rs_list[:semantics_top_n])
    reply_content["c"] = label
    return reply_content


def build_qa_specialty_content(rs_list):
    rs_dict = {}
    rs_len = len(rs_list)
    if rs_len == 0:
        rs_dict["a"] = current_app.config['DEFAULT_ANSWER']
    elif rs_len == 1:
        rs_dict["q"] = rs_list[0][0]
        rs_dict["a"] = rs_list[0][1]
    else:
        q_a_guess = []
        for i, (sq, rs, score, id_) in enumerate(rs_list):
            # q_a_guess.append((sq.replace(" ", ""), rs.replace(" ", ""), score, id_))
            q_a_guess.append((sq, rs, score, id_))
        rs_dict["q_a_guess"] = q_a_guess
    return rs_dict


def build_content(rs_list):
    rs_dict = {}
    rs_len = len(rs_list)
    if rs_len == 0:
        rs_dict["a"] = current_app.config['DEFAULT_ANSWER']
    elif rs_len == 1:
        rs_dict["q"] = rs_list[0][0]
        rs_dict["a"] = rs_list[0][1]
    else:
        q_a_guess = []
        for i, (sq, rs) in enumerate(rs_list):
            if i == 0:
                rs_dict["a"] = rs
            else:
                q_a_guess.append((sq, rs))
        rs_dict["q_a_guess"] = q_a_guess
    return rs_dict


if __name__ == '__main__':
    # 评估
    question_list = [
        ('上个月做了退运已补税未退税证明，税务局给了证明，本月做退运补税证明冲减录入后自助办税提示该报关单美元离岸价超过合理范围怎么处理？', ('27',)),
        ('本公司一批货物原申报了单证不齐，但是没有申报单证齐全，后来超期，税务局要求做视同内销，请问怎么操作？', ('1', '3')),
        ('什么时候需要办理退运已补税未退税证明？', ('23',)),
        ('请问退运已补税未退税证明什么时候需要办理呢？', ('23',)),
        ('单证不齐的冲减应该怎么做啊？', ('3',)),
    ]
    full_correct_counts = 0
    full_error_list = []
    part_correct_counts = 0
    part_error_list = []
    for question, identifiers in question_list:
        # 语义理解
        rs_dict_ = get_reply(['QA_sf'], question)
        if "q_a_guess" not in rs_dict_:
            print("无法回答")
            continue
        guess_list = rs_dict_["q_a_guess"]
        [print(guess) for guess in guess_list]
        print("--------------")
        y_pred_ = [id_ for q, a, s, id_ in guess_list]
        correct_list = [True for id_ in identifiers if id_ in y_pred_]
        if len(correct_list) == len(identifiers):  # 当前测试数据的所需标签【全部】正确匹配
            full_correct_counts += 1
        else:
            full_error_list.append(
                "question:%s\ny_true:%s\nguess_list:%s "
                % (question, identifiers, guess_list))
        if correct_list:  # 当前测试数据的所需标签【部分】正确匹配
            part_correct_counts += 1
        else:
            part_error_list.append(
                "question:%s\ny_true:%s\n guess_list:%s "
                % (question, identifiers, guess_list))
    print("----------------------测试统计如下：----------------------")
    print("测试数据总数：%s" % len(question_list))
    print("- - - - - ")
    print("严格逻辑的正确预测数：%s" % full_correct_counts)
    print("严格逻辑的错误预测数：%s" % (len(question_list) - full_correct_counts))
    print("严格逻辑的正确率：%s" % (full_correct_counts / len(question_list)))
    print("严格逻辑下预测错误的句子===========>")
    [print(err) for err in full_error_list]
    print("- - - - - ")
    print("非严格逻辑的正确预测数：%s" % part_correct_counts)
    print("非严格逻辑的错误预测数：%s" % (len(question_list) - part_correct_counts))
    print("非严格逻辑的正确率：%s" % (part_correct_counts / len(question_list)))
    print("非严格逻辑下预测错误的句子===========>")
    [print(err) for err in part_error_list]
