# -*- coding: utf-8 -*-
"""

Created on June 7, 2019

@author:  neerbek
"""

import os
# os.chdir(os.path.join(os.getenv('HOME'), 'jan/phd/DLP/Monsanto'))
import pandas as pd

import json
import projectSetup
from similarity import load_trees


dataDir = os.path.join(os.getenv('HOME'), 'jan/ProjectsData/phd/DLP/Monsanto/data/trees/20190508/labellings')

labellings = ['session_sophie_sample250_4_labels.json',
              'session_david_sample250_4_labels.json',
              'session_jakob_sample250_4_labels.json']


# [index, short-name, full-name]
LABEL_INDEX = 0
LABEL_SHORT_NAME = 1
LABEL_FULL_NAME = 2
treelabels = [
    [0, 'GHOST', 'Ghostwriting, Peer-Review & Retraction'],
    [1, 'TOXIC', 'Surfactants, Carcinogenicity & Testing'],
    [2, 'CHEMI', 'Absorption, Distribution, Metabolism & Excretion'],
    [3, 'REGUL', 'Regulatory & Government']
]
content = []

for name in labellings:
    filename = os.path.join(dataDir, name)
    with open(filename, 'r') as f:
        c = f.read()
    j = json.loads(c)
    print("loaded", name, "got", len(j))
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
tmp = {}
for mon in monsantoLabelEntries:
    tmp[mon['monsantoId']] = mon
len(tmp)
# 118
monsantoLabelEntries = tmp

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

fileIds = keys[0]  # list of mon fileids, e.g. "MONGLY00971543"

for fid in fileIds:
    j = content[0][fid]  # labellings 0, a list of sentences found in doc fid
    j1 = content[1][fid]
    for j1 in [content[1][fid], content[2][fid]]:  # labellings 1 and 2
        if len(j) != len(j1):
            raise Exception("Number of sentences found for doc id {} in labellings differ {} vs {}".format(fid, len(j), len(j1)))
        for i in range(len(j)):
            sent0 = j[i]
            sent1 = j1[i]
            for entry in ["mon_fileName", "sentenceIndex", "sentence"]:  # these members we expect are the same
                if sent0[entry] != sent1[entry]:
                    raise Exception("mismatch in {} for entry {} (sentence: {}). Expected {}, got {}".format(fid, entry, i, sent0[entry], sent1[entry]))

countLabellers = len(labellings)
derivedContent = []
labels = {}
labelChanged = 0
for j in range(countLabellers):
    curr = content[j]
    derivedContent.append({'labellerIndex': j, 'labellerName': None, 'annotationIndexList': [], 'annotationSentenceMap': {}})
    currLabeller = derivedContent[-1]
    for fid in fileIds:
        for i, sent in enumerate(curr[fid]):
            if sent['annotations'] != None:
                for key, val in sent['annotations'].items():
                    if currLabeller['labellerName'] is None:
                        currLabeller['labellerName'] = val['user']
                    if currLabeller['labellerName'] != val['user']:
                        raise Exception("Found two names for labellerIndex {}, {} and {}".format(currLabeller['labellerIndex'], currLabeller['labellerName'], val['user']))
                    if fid == "MONGLY01832749%20Absorbed%20at%20Higher%20Rate":  # bad id
                        fid = "MONGLY01832749 Absorbed at Higher Rate"
                    if fid == "MONGLY01832749 Absorbed at Higher Rate":
                        val['label'] = treelabels[2][LABEL_FULL_NAME]
                        labelChanged += 1
                    currLabeller['annotationIndexList'].append([fid, i])
                    if val['label'] not in labels:
                        labels[val['label']] = 0
                    labels[val['label']] += 1
                    currLabeller['annotationSentenceMap'][sent['sentence']] = val['label']
                    if fid not in monsantoLabelEntries:
                        print("Missing key", fid)
                        continue
                    mon = monsantoLabelEntries[fid]
                    if mon['label'] != val['label']:
                        print("Mismatch in sensitive labels for {}, user {} got {} expected {}".format(fid, val['user'], val['label'], mon['label']))
print(labels)
# {'Surfactants, Carcinogenicity & Testing': 232, 'Ghostwriting, Peer-Review & Retraction': 253, 'Absorption, Distribution, Metabolism & Excretion': 159, 'Regulatory & Government': 161}
print(labelChanged)
# 9

for dContent in derivedContent:
    print(dContent['labellerIndex'], dContent['labellerName'], len(dContent['annotationIndexList']))
# 0 Sophie 227
# 1 David 294
# 2 Jakob 284

# are there mismatch in labels?

# ######################################################################
# ######################################################################
# ######################################################################

# copied from 20180418 to 20190508
# trees0.zip, trees1.zip, trees2.zip and trees3.zip
dataDir = os.path.join(os.getenv("HOME"), "jan/ProjectsData/phd/DLP/Monsanto/data/trees/20190508")


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
            tree.replace_nodenames('0')   # reset all labels (syntax attribute)

    seen = {}  # sentence to cut
    count = 0
    for trees in treeList:
        tree = treeList[0][0]
        for tree in trees:
            sentence = load_trees.output_sentence(tree)
            for currContent in derivedContent:
                if sentence in currContent['annotationSentenceMap']:
                    count += 1
                    if sentence not in seen:
                        seen[sentence] = 0
                    seen[sentence] += 1
                    label = tree.syntax
                    if label == '0.66':
                        label = '1'
                    elif label == '0.33':
                        label = '0.66'
                    elif label == '0':
                        label = '0.33'
                    else:
                        raise Exception("Unknown label {}".format(label))
                    tree.replace_nodenames(label)
    print(filename, "Done updating trees, count:", count)
    # Done updating trees, count: 470
    m = 0
    total = 0
    for s in seen.keys():
        if seen[s] > m:
            m = seen[s]
        total += seen[s]
    print(filename, "keys", len(seen), "max", m, "total", total)
    # keys 272 max 33 total 470
    # 33 is high - but this is 3 labelers x 11 repeating sentences
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
    # 0.00    6633
    # 0.33     178
    # 0.66      71
    # 1.00      50

    # (+ 178 (* 2 71) (* 3 50))470
    for i, trees in enumerate(treeList):
        count = 0
        for tree in trees:
            if tree.syntax != '0':
                count += 1
        destination = ""
        if i == 0:
            destination = "train"
        elif i == 1:
            destination = "dev"
        elif i == 2:
            destination = "test"
        print(filename, "treeset", destination, "fraction sensitive", "{:.3f}".format(count / len(trees)))
        load_trees.put_trees(os.path.join(dataDir, filename + destination + "_manual_fraction.txt"), trees)

    for trees in treeList:
        for tree in trees:
            label = tree.syntax
            if label != '0':
                tree.replace_nodenames('1')

    for i, trees in enumerate(treeList):
        destination = ""
        if i == 0:
            destination = "train"
        elif i == 1:
            destination = "dev"
        elif i == 2:
            destination = "test"
        load_trees.put_trees(os.path.join(dataDir, filename + destination + "_manual_sensitive.txt"), trees)
