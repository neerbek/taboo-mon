# -*- coding: utf-8 -*-
"""

Created on June 7, 2019

@author:  neerbek
"""

# copy of SessionReader.py - this one only saves train, dev, test we labels with know.

import os
# os.chdir(os.path.join(os.getenv('HOME'), 'jan/phd/DLP/Monsanto'))
import pandas as pd

import json
import projectSetup
from similarity import load_trees


dataDir = os.path.join(os.getenv('HOME'), 'jan/ProjectsData/phd/DLP/Monsanto/data/trees/20190621/labellings')

labellings = ['session_sophie_sample250_4_labels.json',
              'session_david_sample250_4_labels.json',
              'session_jakob_sample250_4_labels.json']


treelabels = [
    {'index': 0, 'short': 'GHOST', 'full': 'Ghostwriting, Peer-Review & Retraction'},
    {'index': 1, 'short': 'TOXIC', 'full': 'Surfactants, Carcinogenicity & Testing'},
    {'index': 2, 'short': 'CHEMI', 'full': 'Absorption, Distribution, Metabolism & Excretion'},
    {'index': 3, 'short': 'REGUL', 'full': 'Regulatory & Government'}
]
content = []

for name in labellings:
    filename = os.path.join(dataDir, name)
    with open(filename, 'r') as f:
        c = f.read()
    j = json.loads(c)
    print("loaded", name, "got", len(j), "document keys")
    content.append(j)

# loaded session_sophie_sample250_4_labels.json got 97
# loaded session_david_sample250_4_labels.json got 97
# loaded session_jakob_sample250_4_labels.json got 97

dataDir = os.path.join(os.getenv("HOME"), "jan/taboo/taboo-mon")
filename = os.path.join(dataDir, "monsantoLabelEntries.json")
with open(filename, 'r') as f:
    c = f.read()
    monsantoLabelEntries = json.loads(c)

print(len(monsantoLabelEntries))
# 118
tmp = {}  # mon doc Id -> monsantoLabelEntry
for mon in monsantoLabelEntries:
    tmp[mon['monsantoId']] = mon
len(tmp)
# 118
monsantoLabelEntries = tmp   # mon doc Id -> monsantoLabelEntry
# monsantoLabelEntries['MONGLY02286842']['label']

# sanity check that at all labellings have same id's
keys = []
for c in content:
    mylist = list(c.keys())
    mylist.sort()
    keys.append(mylist)

if keys[0] != keys[1]:
    raise Exception("mismatch for list 0 and 1")
if keys[1] != keys[2]:
    raise Exception("mismatch for list 1 and 2")
# sorted keys (mon-id) are the same for labellings 0, 1 and 2

monIdList = keys[0]

# sanity check that labellings contain same sentences
labelChanged = 0
sentenceLabelMap = {}  # map from sentence to last seen label category
fid = 'ACQUAVELLAPROD00008909'
for fid in monIdList:
    # print("fid", fid)
    j = content[0][fid]  # labellings 0, a list of sentences found in doc fid
    j1 = content[1][fid]
    for j1 in [content[1][fid], content[2][fid]]:  # labellings 1 and 2
        if len(j) != len(j1):
            raise Exception("Number of sentences found for doc id {} in labellings differ {} vs {}".format(fid, len(j), len(j1)))
        i = 0
        for i in range(len(j)):
            sent0 = j[i]
            sent1 = j1[i]
            for entry in ["mon_fileName", "sentenceIndex", "sentence"]:  # these members we expect are the same
                if sent0[entry] != sent1[entry]:
                    raise Exception("mismatch in {} for entry {} (sentence: {}). Expected {}, got {}".format(fid, entry, i, sent0[entry], sent1[entry]))
            s = sent0
            for s in [sent0, sent1]:
                if s['annotations'] is None:
                    raise Exception("None annotations not allowed in {}".format(s))
                # key = list(s['annotations'].keys())[0]
                # val = s['annotations'][key]
                for key, val in s['annotations'].items():
                    if fid == "MONGLY01832749%20Absorbed%20at%20Higher%20Rate":  # bad id
                        val['label'] = treelabels[2]['full']
                        labelChanged += 1
                        expectedLabel = treelabels[2]['full']
                    else:
                        expectedLabel = monsantoLabelEntries[fid]['label']
                    if expectedLabel != val['label']:
                        raise Exception("Mismatch in sensitive labels for {}, user {} got {} expected {}".format(fid, val['user'], val['label'], expectedLabel))
                    if s['sentence'] not in sentenceLabelMap:
                        sentenceLabelMap[s['sentence']] = expectedLabel
                    if sentenceLabelMap[s['sentence']] != expectedLabel:
                        raise Exception("Sentence '{}' has two labels".format(s['sentence'], sentenceLabelMap[s['sentence']], expectedLabel))

print("labelsChanged:", labelChanged)
# labelsChanged: 14
len(sentenceLabelMap)
# 414
# all labellings passed sanity test

countLabellers = len(labellings)
labelsCount = [0, 0, 0]
annotationsCount = [0, 0, 0]
labelsSum = [0, 0, 0]
sentenceMap = {}  # sentence to label (0, 33, 66, 100)
j = 0
for j in range(countLabellers):
    curr = content[j]  # map doc-id to (possible) labels by labeller index j
    # all keys for curr is in monIdList by sanity check above
    # mid = monIdList[0]
    for mid in monIdList:
        # i = 1
        # sent = curr[mid][i]
        for i, sent in enumerate(curr[mid]):
            if sent['sentence'] not in sentenceMap:
                sentenceMap[sent['sentence']] = 0
            if len(sent['annotations']) != 0:
                labelsCount[j] += 1
                for key, val in sent['annotations'].items():
                    annotationsCount[j] += 1
                previous = sentenceMap[sent['sentence']]
                if previous < 100:  # 100 is max (repeating sentences)
                    previous += 33
                    labelsSum[j] += 33
                if previous == 99:
                    previous = 100
                    labelsSum[j] += 1
                sentenceMap[sent['sentence']] = previous
count = 0
countNotZero = 0
for key, val in sentenceMap.items():
    count += val
    if val > 0:
        countNotZero += 1
print(count, (284 + 294 + 227), (284 + 294 + 227) * 33, countNotZero, len(sentenceMap))
# 21879 805 26565 414 982
print(labelsCount, annotationsCount, labelsSum)
# [193, 234, 236] [227, 294, 284] [6369, 7723, 7787]
# 0 Sophie 227
# 1 David 294
# 2 Jakob 284
sum(labelsSum)
# 21879

# ok it seems

# ######################################################################
# ######################################################################
# ######################################################################

# copied from 20180418 to 20190815
# trees0.zip, trees1.zip, trees2.zip and trees3.zip
dataDir = os.path.join(os.getenv("HOME"), "jan/ProjectsData/phd/DLP/Monsanto/data/trees/20190815")

filename = 'trees0'
for filename in ['trees0', 'trees1', 'trees2', 'trees3']:
    origTreeList = []
    origTreeList.append(load_trees.get_trees(os.path.join(dataDir, filename + ".zip$train.txt")))
    origTreeList.append(load_trees.get_trees(os.path.join(dataDir, filename + ".zip$dev.txt")))
    origTreeList.append(load_trees.get_trees(os.path.join(dataDir, filename + ".zip$test.txt")))

    treeList = []
    treeList.append(load_trees.get_trees(os.path.join(dataDir, filename + ".zip$train.txt")))
    treeList.append(load_trees.get_trees(os.path.join(dataDir, filename + ".zip$dev.txt")))
    treeList.append(load_trees.get_trees(os.path.join(dataDir, filename + ".zip$test.txt")))

    for trees in treeList:
        tree = treeList[0][0]
        for tree in trees:
            tree.replace_nodenames(-1)   # reset all labels (syntax attribute)

    print(filename, len(treeList))
    print(filename, len(treeList[0]), len(treeList[1]), len(treeList[2]))
    # trees0 3
    # trees0 5900 500 532
    seen = {}  # sentence to cut
    count = 0
    for i, trees in enumerate(treeList):
        tree = treeList[0][0]
        for tree in trees:
            sentence = load_trees.output_sentence(tree)
            if sentence in sentenceMap:
                count += 1
                if sentence not in seen:
                    seen[sentence] = 0
                seen[sentence] += 1
                label = sentenceMap[sentence]
                label /= 100
                tree.replace_nodenames(label)

    for i in range(len(treeList)):
        orig_trees = treeList[i]
        trees = [tree for tree in orig_trees if tree.syntax > -1]
        treeList[i] = trees
        print(filename, "Done updating trees, count:", count, len(orig_trees), len(trees))
    treeLabels = []
    for trees in treeList:
        for tree in trees:
            treeLabels.append(float(tree.syntax))

    origTreeLabels = []
    for trees in origTreeList:
        for tree in trees:
            origTreeLabels.append(float(tree.syntax))
    treeLabels = pd.Series(treeLabels)
    origTreeLabels = pd.Series(origTreeLabels)

    print(filename, origTreeLabels.value_counts())
    # 0.0    3466
    # 1.0    3466

    print(filename, treeLabels.value_counts())
    #     trees0 0.00    428
    # 0.33    167
    # 0.66     80
    # 1.00     52
    destinations = ["train", "dev", "test"]
    for i, destination in enumerate(destinations):
        trees = treeList[i]
        count = 0
        for tree in trees:
            if tree.syntax > 0:
                count += 1
            tree.replace_nodenames('{:.2f}'.format(tree.syntax))
        print(filename, "treeset", destination, "fraction sensitive", "{:.3f}".format(count / len(trees)))
        load_trees.put_trees(os.path.join(dataDir, filename + destination + "_manual_fraction.txt"), trees)
        # trees0 treeset train fraction sensitive 0.418
        # put_trees done. Count=625
        # trees0 treeset dev fraction sensitive 0.362
        # put_trees done. Count=58
        # trees0 treeset test fraction sensitive 0.386
        # put_trees done. Count=44

    for i, destination in enumerate(destinations):
        trees = treeList[i]
        count = 0
        for tree in trees:
            label = tree.syntax
            if label != '0.00':
                tree.replace_nodenames('1')  # weigths 0 or 1
                count += 1
        print(filename, "treeset", destination, "fraction sensitive", "{:.3f}".format(count / len(trees)))
        load_trees.put_trees(os.path.join(dataDir, filename + destination + "_manual_sensitive.txt"), trees)
