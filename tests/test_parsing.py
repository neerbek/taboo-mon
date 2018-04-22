# -*- coding: utf-8 -*-
"""

Created on April 18, 2018

@author:  neerbek
"""

import unittest

import tests.RunTimer  # from taboo-core

import monUtil
import server_rnn_helper
import rnn_enron

from similarity import load_trees

# from monexp-2018-04-17-15-39-01.log
case1 = "__ __ comment -LSB- wh17J; JOHN IS WRONG- IT IS THERE IT IS THE 3 ONE MENTIONED BY HILL 1 Comment Strong\nin Hill article refers i I I to the size of the difference between exposure I groups, not presenoelabsenc\ne of statistical I_ significance_,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n, -RRB- 2_ The association is not consistent, since four out of five mouse studies did not similar renal\nneoplasms at comparable doses_ 3_ The association is not specific,, since females of this pivotal study,\nwhich have been exposed to higher levels of glyphosate did not develop renal neoplasms_ Also, there were\nno renal findings in the LO group, whereas the control group had two_ Comment This is not what Hill meant\n I by specificity."

# removing complexity to make faster
case2 = "Not presenoelabsence of statistical significance_,,,,,,\n,. The association is not consistent."

case3 = "Not presenoelabsence of statistical significance_,\n,. The association is not consistent."

class TestNLTKParser(unittest.TestCase):
    def setUp(self):
        self.timer = tests.RunTimer.Timer()

    def tearDown(self):
        self.timer.report(self, __file__)

    def test_one(self):
        sentences = server_rnn_helper.get_indexed_sentences(case3)
        print("number of split sentences are: ", len(sentences))
        for sentence in sentences:
            sentence.sentence = sentence.sentence.replace("\n", "")
        # sentences = [sentences[0]]
        parserStatistics = rnn_enron.ParserStatistics()
        trees = server_rnn_helper.get_nltk_trees(0, sentences, parserStatistics)
        self.assertEqual(len(sentences), len(trees))
        if parserStatistics.emptySubTrees > 0:
            print("Could not parse subtree, aborting test")
            return
        i = 0
        for i in range(len(sentences)):
            if sentences[i].sentence != load_trees.output_sentence(trees[i])[1:]:
                print("sentences differ")
                print("orig:", sentences[i].sentence)
                print("gene:", load_trees.output_sentence(trees[i]))
                self.assertEqual(sentences[i].sentence, load_trees.output_sentence(trees[i])[1:])  # fails

    def test_two(self):
        # TODO: enable support for 's
        mycase = "'s have LONG delays to get results."
        mycase = "s have LONG delay's to get results."
        mycase = monUtil.removeApostrof(mycase)
        sentences = server_rnn_helper.get_indexed_sentences(mycase)
        print("number of split sentences are: ", len(sentences))
        self.assertEqual(1, len(sentences))
        parserStatistics = rnn_enron.ParserStatistics()
        trees = server_rnn_helper.get_nltk_trees(0, sentences, parserStatistics)
        self.assertEqual(sentences[0].sentence, load_trees.output_sentence(trees[0])[1:])

    def test_three(self):
        mycase = case2
        mycase = monUtil.removeNewline(mycase)
        mycase = monUtil.removeMultiCommas(mycase)
        print(mycase)
        sentences = server_rnn_helper.get_indexed_sentences(mycase)
        print("number of split sentences are: ", len(sentences))
        self.assertEqual(2, len(sentences))
        parserStatistics = rnn_enron.ParserStatistics()
        trees = server_rnn_helper.get_nltk_trees(0, sentences, parserStatistics)
        self.assertEqual(sentences[0].sentence, load_trees.output_sentence(trees[0])[1:])
        self.assertEqual(sentences[1].sentence, load_trees.output_sentence(trees[1])[1:])


if __name__ == "__main__":
    unittest.main()
