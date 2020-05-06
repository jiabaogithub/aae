import unittest

from conftest import CheckChatterbot, CheckIntentClassifier


'''
调整了txt中的内容后，对应的chatterbot要进行再学习，文本-向量索引文件要重新生成，分类器要重新训练
'''
if __name__ == '__main__':
    suite = unittest.TestSuite()
    tests = [
        CheckIntentClassifier('test_full_retrain_clf'),
        # CheckIntentClassifier('test_evaluate_clf')
        # CheckChatterbot('test_train_sf'), # ······ 记得先禁用sf.py中的ChatBot的preprocessors，原因同下
        # CheckChatterbot('test_train_talk'), #······ 记得先禁用custom_chatbot.py中的ChatBot的preprocessors(注入了一个文本向量化的操作)，该方法在chatbot训练的时候也会被触发，在启动系统前，记得恢复，否则语义匹配阶段输入文本不会向量化
        # CheckChatterbot('test_build_text_vec_indx'),
        # CheckChatterbot('test_learn'),
    ]
    suite.addTests(tests)
    runner = unittest.TextTestRunner()
    runner.run(suite)
