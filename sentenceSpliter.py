# -*- coding: utf-8 -*-
"""

Created on April 12, 2018

@author:  neerbek
"""

import os
import getopt
import sys

import io

import monUtil
import monsantoData
import textClean
import server_rnn_helper
from similarity import load_trees

from importlib import reload
reload(textClean)
# from backends import PDFMinerBackend
datadir = "../data_monsanto/2018-04-12-workdir"
filename = "monsantoDataEntries.json"
startindex = 0
endindex = -1
outfile = "indexedsentences.txt"

def usage(exitCode=0):
    print('sentenceSplitter.py [-o <outputfile>] [-d datadir] [-l <labelfile>] [-s <startindex>] [-e <endindex] [-h]')
    sys.exit(exitCode)


# parse input
argv = sys.argv[1:]  # first arg is filename
# argv = "-s 0 -e -1 -o jantmp_trees.txt".split()
try:
    opts, args = getopt.getopt(argv, "hd:l:s:e:o:", ["help", "datadir=", "labelfile=", "start=", "end=", "outfile="])
except getopt.GetoptError:
    usage(exitCode=2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage(exitCode=0)
    elif opt in ("-d", "--datadir"):
        datadir = arg
    elif opt in ("-l", "--labelfile"):
        filename = arg
    elif opt in ("-s", "--start"):
        startindex = int(arg)
    elif opt in ("-e", "--end"):
        endindex = int(arg)
    elif opt in ("-o", "--outfile"):
        outfile = arg

labelMap = {}
for i, label in enumerate(monsantoData.labelList):
    labelMap[label] = i

docs = monUtil.loadJSONList(filename, monUtil.MonsantoDocument.dictToMonsantoDocument)
for d in docs:
    d.uri = os.path.join(datadir, d.uri[:-4] + ".txt")
    d.label = labelMap[d.label]

# want to address
# non-ascii
# sentences split over several lines (with newlines)
# monIds in text
# non-informative lines (maybe later)
# save with docId (monId?) and with lineNumber and sentenceNumber
# I guess to save in file next to datafile with extension .sentences (might cause problems on windows)
# watch out for very long or very short sentences

cleanDocs = []
for i, doc in enumerate(docs):
    doc = docs[i]
    doc.uri = doc.uri.replace("\ ", " ")   # don't escape for io.open
    doc.uri = doc.uri.replace("\$", "$")   # don't escape for io.open
    with io.open(doc.uri, 'r', encoding='utf8') as f:
        lines = f.readlines()
    cleaner = textClean.TextCleaner()
    res = []
    for j, line in enumerate(lines):
        before = line
        line = cleaner.cleanLine(line)
        if len(line) != 0:
            res.append(line)
    cleanDocs.append(res)
    if len(res) == 0:
        print("INFO: received empty doc: ", i, doc.uri)
    # if i % 10 == 0:
    # print("INFO: done processing doc", i)


indexedSentenceList = []
for i, text in enumerate(cleanDocs):
    sentences = server_rnn_helper.get_indexed_sentences("\n".join(text))
    for sentence in sentences:
        sentence.sentence = monUtil.removeNewline(sentence.sentence)  # remove \n introduced above, not handled by server_rnn_helper.get_nltk_trees below
        sentence.sentence = monUtil.removeApostrof(sentence.sentence)  # remove "'" not handled by server_rnn_helper.get_nltk_trees below
        sentence.sentence = monUtil.removeMultiCommas(sentence.sentence)  # remove multiple commas
    indexedSentenceList.append(sentences)

# i = 0
# for indexedSentence in indexedSentenceList[i]:
#     print(indexedSentence)

# count = 0
# for sentences in indexedSentenceList:
#     count += len(sentences)
# print(count)
# counts = []
# for sentences in indexedSentenceList:
#     for sentence in sentences:
#         counts.append(len(sentence.sentence))
# len(counts)
# import numpy
# data = numpy.array(counts)
# print(max(counts))
# bins = numpy.array([5, 20, 75, 125, 300, 500, 1000])
# classes = numpy.digitize(data, bins)
# unique, counts = numpy.unique(classes, return_counts=True)
# print(dict(zip(unique, counts)))
# # {0: 1175, 1: 1122, 2: 2428, 3: 2062, 4: 3165, 5: 573, 6: 195, 7: 54}

# count = 0
# val = 1
# for c in counts:
#     if c == val:
#         count += 1
# print("{}:".format(val), count)


treeList = []
if endindex == -1:
    endindex = len(indexedSentenceList)
endindex = min(endindex, len(indexedSentenceList))

for i in range(startindex, endindex):
    indexSentences = indexedSentenceList[i]
    print("Working on doc {}/{} ({}-{})".format(i, len(indexedSentenceList), startindex, endindex))
    trees = server_rnn_helper.get_nltk_trees(i, indexedSentenceList[i])
    treeList.append(trees)
    if len(trees) == 0:
        print("WARN: trees were empty", i, docs[i].uri)

trees = []
for i in range(startindex, endindex):
    doc = docs[i]
    indexSentences = indexedSentenceList[i]
    for indexSentence in indexSentences:
        tree = indexSentence.tree
        if tree is None:
            continue  # empty tree
        n = load_trees.Node()
        n.syntax = "{}".format(indexSentence.beginIndex)
        n.word = doc.monsantoId
        n.word = n.word.replace(" ", "%20")
        tree.parent = n
        n.left = tree
        nRight = n.add_child()
        nRight.syntax = "{}".format(doc.label)
        nRight.word = doc.uri[len(datadir) + 1:-4]
        nRight.word = nRight.word.replace(" ", "%20")
        trees.append(n)

load_trees.put_trees(outfile, trees)
# TODO: add timestamp here so we can track when the process terminated
print("done. saved {} trees to {}".format(len(trees), outfile))
