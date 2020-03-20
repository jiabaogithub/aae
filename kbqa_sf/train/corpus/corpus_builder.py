# -*- coding: utf-8 -*-

"""
本模块用于构建问题语料库
"""
import codecs

import jieba

import path_configer
from kbqa_sf.sentence_processer import SentenceProcesser

__author__ = '程序员涤生'

import os.path
import jieba.analyse


def build_corpus_vocabulary():
    data_root_dir = path_configer.get_classifier_train_samples()
    w_path = "%s/question.txt" % path_configer.get_resources_corpus()
    if os.path.exists(w_path):
        os.remove(w_path)
    for file in os.listdir(data_root_dir):
        path = os.path.join(data_root_dir, file)
        q_list = []
        print("开始读取文件:%s" % file)
        with codecs.open(path, "r", encoding="utf-8") as f:
            line = f.readline()
            line = line.strip("\n\r")
            while line != "":
                q_list.append(line[line.find(" ") + 1:])
                line = f.readline()
                line = line.strip("\n\r")
        print("开始写入文本%s" % w_path)
        with codecs.open(w_path, "a", encoding="utf-8") as f:
            for item in q_list:
                if len(item.strip()) > 0:
                    f.write('%s\n' % item)


def cut_corpus_vocabulary():
    original_path = "%s/question.txt" % path_configer.get_resources_corpus()
    seg_path = "%s/question_seg.txt" % path_configer.get_resources_corpus()
    # 加载自定义分词表
    SentenceProcesser()
    word_list = []
    finput = codecs.open(original_path, "r", encoding="utf-8")
    foutput = codecs.open(seg_path, 'w', encoding='utf-8')
    for line in finput:
        # line_seg = jieba.analyse.extract_tags(line, 20)
        line_seg = jieba.cut(line)
        word_list.extend(line_seg)
    word_set = set(word_list)
    print(word_set)
    for word in word_set:
        if word.strip('\n\r\ufeff').replace(" ", "") == "":
            continue
        foutput.write("%s\n" % word)
    finput.close()
    foutput.close()


if __name__ == '__main__':
    pass
