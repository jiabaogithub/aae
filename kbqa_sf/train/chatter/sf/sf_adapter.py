# -*- coding: utf-8 -*-

"""
扩展chatterbot的BestMatchLogicAdapter
"""
from flask import current_app

__author__ = '程序员涤生'


import logging

from chatterbot.logic import LogicAdapter


class BestMatchExtLogicAdapter(LogicAdapter):
    """
    A logic adapter that returns a response based on known responses to
    the closest matches to the input statement.
    """

    def get(self, input_statement):
        """
        Takes a statement string and a list of statement strings.
        Returns the closest matching statement from the list.
        """
        # '程序员涤生' 多返回了一个所有句子的向量表示statement_vec
        statement_list, statement_vec = self.chatbot.storage.get_response_statements()

        if not statement_list:
            if self.chatbot.storage.count():
                # Use a randomly picked statement
                self.logger.info(
                    'No statements have known responses. ' +
                    'Choosing a random response to return.'
                )
                random_response = self.chatbot.storage.get_random()
                random_response.confidence = 0
                return random_response
            else:
                raise self.EmptyDatasetException()

        closest_match = input_statement
        closest_match.confidence = 0

        closest_match_list = []

        # 利用向量化的方式并行计算相似度
        import numpy as np
        confidence_vec = self.compare_statements(input_statement, statement_vec)
        indx_for_confidence_tuple = np.where(confidence_vec >= current_app.config[
            'THRESHOLD_SEMANTICS_UNDERSTANDER'])  # 筛选出大于阈值的值得索引,返回的是一个元组，元组只有一个元素是一个索引组成的ndarray
        if len(indx_for_confidence_tuple) == 0:
            return closest_match
        indx_for_confidence = indx_for_confidence_tuple[0]
        if indx_for_confidence.size == 0:
            logging.debug("sf领域语义理解在正常置信度阈值下没有匹配到任何项，进行降级匹配...")
            indx_for_confidence_tuple = np.where(confidence_vec >= current_app.config[
                'MINIMUM_THRESHOLD_SEMANTICS_UNDERSTANDER'])  # 降级筛选,返回的是一个元组，元组只有一个元素是一个索引组成的ndarray
            indx_for_confidence = indx_for_confidence_tuple[0]
        for i in indx_for_confidence:  # 这里只涉及到大于阈值的句子的遍历，所以不会很多,除非阈值设定的非常低
            confidence = confidence_vec[i]
            statement = statement_list[i]
            # logging.debug("text:%s, 置信度：%s", statement.text, confidence)
            statement.confidence = confidence
            closest_match = statement
            closest_match_list.append(statement)

        # # Find the closest matching known statement 注释原因：单纯用for循环的效率非常低
        # for statement in statement_list:
        #     confidence = self.compare_statements(input_statement, statement)
        #     logging.debug("置信度：%s", confidence)
        #     if confidence >= current_app.config['THRESHOLD_SEMANTICS_UNDERSTANDER']:
        #         statement.confidence = confidence
        #         closest_match = statement
        #         closest_match_list.append(statement)
        # if len(closest_match_list) == 0: # 若没有匹配就降低阈值，以便兜底
        #     logging.debug("sf领域语义理解在正常置信度阈值下没有匹配到任何项，进行降级匹配...")
        #     for statement in statement_list:
        #         confidence = self.compare_statements(input_statement, statement)
        #         logging.debug("置信度：%s", confidence)
        #         if confidence >= current_app.config['MINIMUM_THRESHOLD_SEMANTICS_UNDERSTANDER']:
        #             statement.confidence = confidence
        #             closest_match = statement
        #             closest_match_list.append(statement)
        closest_match_list.sort(key=lambda x: x.confidence, reverse=True)
        n = 3
        closest_match.closest_match_list = closest_match_list[:n]  # 取topN个最匹配的
        logging.debug("===================top%s个最匹配的问题：", n)
        for item in closest_match.closest_match_list:
            logging.debug("===================问题：%s, 置信度：%s", item.text, item.confidence)
        return closest_match

    def can_process(self, statement):
        """
        Check that the chatbot's storage adapter is available to the logic
        adapter and there is at least one statement in the database.
        """
        return self.chatbot.storage.count()

    def process(self, input_statement):

        # Select the closest match to the input statement
        closest_match = self.get(input_statement)
        self.logger.info('Using "{}" as a close match to "{}"'.format(
            input_statement.text, closest_match.closest_match_list
        ))
        list_ = closest_match.closest_match_list
        response_closest_list = []
        response = None
        for closest_match in list_:
            # 若匹配到的是答案，就返回当前答案对象自身做为一个响应对象
            if closest_match.text.startswith("A "):
                # if int(closest_match.text[:closest_match.text.find(' ')]) % 2 == 0:  # 单数是问题，双数是答案
                response = closest_match
                response_closest_list.append(response)
            else:
                # Get all statements that are in response to the closest match
                response_list = self.chatbot.storage.filter(
                    in_response_to__contains=closest_match.text,
                    # '程序员涤生' 设置该参数会让存储器按创建日期倒序排列某个问题的多个不同答案，以便实现修订问题的需求
                    order_by = 'created_at'
                )

                if response_list:
                    self.logger.info(
                        'Selecting response from {} optimal responses.'.format(
                            len(response_list)
                        )
                    )
                    response = self.select_response(input_statement, response_list)
                    response.confidence = closest_match.confidence
                    irt_list = response.in_response_to
                    response.in_response_to = [r for r in irt_list if r.text==closest_match.text]
                    # response.question = closest_match.text
                    response_closest_list.append(response)
                    self.logger.info('Response selected. Using "{}"'.format(response.text))
                else:
                    response = self.chatbot.storage.get_random()
                    self.logger.info(
                        'No response to "{}" found. Selecting a random response.'.format(
                            closest_match.text
                        )
                    )

                    # Set confidence to zero because a random response is selected
                    response.confidence = 0
        if not response:
            response = self.chatbot.storage.get_random()
            self.logger.info(
                'No response to "{}" found. Selecting a random response.'.format(
                    closest_match.text
                )
            )

            # Set confidence to zero because a random response is selected
            response.confidence = 0
            response.response_closest_list = []
        else:
            response.response_closest_list = response_closest_list
        return response
