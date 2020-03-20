import unittest

from chatterbot.conversation import Statement

import kbqa_config as kc
from kbqa_sf.kbqa.flaskr import create_app, loadProjContext
from kbqa_sf.sentence_processer import SentenceProcesser
from kbqa_sf.train.chatter.custom.custom_chatbot import train_custom_chatbot
from kbqa_sf.train.chatter.sf.sf import train_sf_chatbot, SF
from kbqa_sf.train.classifier.intent_classifier import IntentClassifier


class CheckChatterbot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("加载flask上下文...")
        create_app(kc.config['testing'])
        print("加载项目上下文...")
        loadProjContext()

    def test_train_sf(self):
        train_sf_chatbot()

    def test_train_talk(self):
        train_custom_chatbot()

    def test_build_text_vec_indx(self):
        # 构建文本-向量索引文件，并存储
        IntentClassifier().build_text_vec_indx()

    def test_learn(self):
        print("测试学习...")
        chatbot_ = SF().chatters['QA_sf_As_domestic_sales']
        # 不同问题、不同答案
        # a = Statement('A 现在v1')
        # q = Statement('Q 什么时候？v1')
        # 相同问题，不同答案
        a = Statement('A bbb')
        q = Statement('Q 你是谁？')
        #
        # # 不同问题、相同答案
        # a = Statement('A 好的')
        # q = Response('Q 看看')
        chatbot_.learn_response(a, q)


class CheckIntentClassifier(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("加载flask上下文...")
        create_app(kc.config['testing'])
        # 加载自定义分词表
        SentenceProcesser()

    def test_full_retrain_clf(self):
        print("完整的训练分类器模型...")
        IntentClassifier().full_retrain_clf()

    def test_evaluate_clf(self):
        clf = IntentClassifier().load_clf()
        clf.evaluate_clf(3)
        # clf.evaluate_clf(5)
        # clf.evaluate_clf(1)


if __name__ == '__main__':
    unittest.main()
