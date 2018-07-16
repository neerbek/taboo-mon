# -*- coding: utf-8 -*-
"""

Created on April 22, 2018

@author:  neerbek
"""

import monUtil
import ai_util
import util
from numpy.random import RandomState  # type: ignore


from similarity import load_trees

from importlib import reload
# reload(load_trees)
# reload(monUtil)
reload(ai_util)
allTreesFile = "../data_monsanto/trees/20180418/all_trees.txt"
allTrees = load_trees.get_trees(allTreesFile)
# get_trees done. Count=9827. Roots with words count 9827

trees = [monUtil.MonsantoTree(t) for t in allTrees]
load_trees.put_trees("tmp.txt", [t.asSingleTree() for t in trees])
# diff tmp.txt ../data_monsanto/trees/20180418/all_trees.txt
# (no diff)

# allTrees = load_trees.cleanTreesByLength(allTrees, 5, 202)  # added two from artifical nodes
# # cleanTreesByLength: removed short 1653, removed long 35. Previous 9827 New length 8139
# allTrees = load_trees.cleanTreesByLength(allTrees, 6, 202)  # added two from artifical nodes
# # cleanTreesByLength: removed short 1931, removed long 35. Previous 9827 New length 7861
allTrees = load_trees.cleanTreesByLength(allTrees, 7, 202)  # added two from artifical nodes
# cleanTreesByLength: removed short 2173, removed long 35. Previous 9827 New length 7619
allTrees = load_trees.cleanTreesByBadChars(allTrees)
# cleanTreesByBadChars Cleaned: 0

trees = [monUtil.MonsantoTree(t) for t in allTrees]
rawTrees = [monUtil.MonsantoTree(load_trees.clone_tree(t)) for t in allTrees]
print(len(trees), len(rawTrees))
# 7619 7619
for t in rawTrees:
    t.tree.replace_nodenames("{}".format(t.label))
baseTrees = [t.tree for t in rawTrees]
len(baseTrees), len(rawTrees)
# baseTrees = cleaner.cleanAmbigous(baseTrees)
cleaner = load_trees.SentenceCounter(baseTrees, ["0", "1", "2", "3"])
res = []
for t in rawTrees:
    sentence = load_trees.output_sentence(t.tree)
    if not cleaner.isSentenceAmbigous(sentence, "{}".format(t.label)):
        res.append(t)
cleaner.reportFindings()
# contented 181 ignored 82. New size 7537
trees = res
len(trees)
# 7537 (orig: 9827)

# ## length buckets
counts = []
for t in trees:
    counts.append(load_trees.count_leaf_nodes(t.tree))
len(counts)
import numpy
data = numpy.array(counts)
print(max(counts))
print(min(counts))
bins = numpy.array([6, 10, 20, 30, 40, 50, 75, 100, 150, 202])
classes = numpy.digitize(data, bins)
unique, counts = numpy.unique(classes, return_counts=True)
print(dict(zip(unique, counts)))
# {0: 1175, 1: 1122, 2: 2428, 3: 2062, 4: 3165, 5: 573, 6: 195, 7: 54}
# punctuation '.' counts as "word"


labels = [t.label for t in trees]
labelSet = set(labels)
print(labelSet)
# {0, 1, 2, 3}

trees0orig = [t for t in trees if t.label == 0]
trees1orig = [t for t in trees if t.label == 1]
trees2orig = [t for t in trees if t.label == 2]
trees3orig = [t for t in trees if t.label == 3]
trees0 = [t for t in trees if t.label == 0]
trees1 = [t for t in trees if t.label == 1]
trees2 = [t for t in trees if t.label == 2]
trees3 = [t for t in trees if t.label == 3]
print(len(trees), len(trees0), len(trees1), len(trees2), len(trees3))
print(len(trees0) + len(trees1) + len(trees2) + len(trees3))
# before filtering
# 9827 4093 1680 2309 1745
# 9827
# after filtering
# 7537 3466 1446 1351 1274
# 7537

def addNegativeSamples(posTrees, negTreesList, randomState=RandomState(87)):
    """Add random elements to posTrees from negTreesList"""
    negTrees = []
    for tmp in negTreesList:
        negTrees.extend(tmp)
    negTrees = ai_util.shuffleList(negTrees, randomState)
    posTrees.extend(negTrees[:len(posTrees)])  # double size


addNegativeSamples(trees0, [trees1orig, trees2orig, trees3orig], RandomState(4547))
addNegativeSamples(trees1, [trees0orig, trees2orig, trees3orig], RandomState(4023))
addNegativeSamples(trees2, [trees1orig, trees0orig, trees3orig], RandomState(3738))
addNegativeSamples(trees3, [trees1orig, trees2orig, trees0orig], RandomState(3043))


trees0 = ai_util.shuffleList(trees0, RandomState(347))
trees1 = ai_util.shuffleList(trees1, RandomState(384))
trees2 = ai_util.shuffleList(trees2, RandomState(748))
trees3 = ai_util.shuffleList(trees3, RandomState(630))

print(2 * len(trees), len(trees0), len(trees1), len(trees2), len(trees3))
print(len(trees0) + len(trees1) + len(trees2) + len(trees3))
# 15074 6932 2892 2702 2548
# 15074
# before filtering
# 19654 8186 3360 4618 3490
# 19654

trees0Train = trees0[:5900]
trees0Val = trees0[5900:6400]
trees0Test = trees0[6400:]

trees1Train = trees1[:2200]
trees1Val = trees1[2200:2540]
trees1Test = trees1[2540:]

trees2Train = trees2[:2100]
trees2Val = trees2[2100:2400]
trees2Test = trees2[2400:]

trees3Train = trees3[:1950]
trees3Val = trees3[1950:2250]
trees3Test = trees3[2250:]

print(len(trees0), len(trees0Train) + len(trees0Val) + len(trees0Test), len(trees0Train), len(trees0Val), len(trees0Test))
print(len(trees1), len(trees1Train) + len(trees1Val) + len(trees1Test), len(trees1Train), len(trees1Val), len(trees1Test))
print(len(trees2), len(trees2Train) + len(trees2Val) + len(trees2Test), len(trees2Train), len(trees2Val), len(trees2Test))
print(len(trees3), len(trees3Train) + len(trees3Val) + len(trees3Test), len(trees3Train), len(trees3Val), len(trees3Test))

# 6932 6932 5900 500 532
# 2892 2892 2200 340 352
# 2702 2702 2100 300 302
# 2548 2548 1950 300 298

def printPositives(full, train, val, test, label):
    res = []
    tmp = [t for t in full if t.label == label]
    res.append(len(tmp))
    tmp = [t for t in train if t.label == label]
    res.append(len(tmp))
    tmp = [t for t in val if t.label == label]
    res.append(len(tmp))
    tmp = [t for t in test if t.label == label]
    res.append(len(tmp))
    print(res[0], res[1] + res[2] + res[3], res[1], res[2], res[3])

def printNegatives(full, train, val, test, label):
    res = []
    tmp = [t for t in full if t.label != label]
    res.append(len(tmp))
    tmp = [t for t in train if t.label != label]
    res.append(len(tmp))
    tmp = [t for t in val if t.label != label]
    res.append(len(tmp))
    tmp = [t for t in test if t.label != label]
    res.append(len(tmp))
    print(res[0], res[1] + res[2] + res[3], res[1], res[2], res[3])


printPositives(trees0, trees0Train, trees0Val, trees0Test, 0)
printNegatives(trees0, trees0Train, trees0Val, trees0Test, 0)
printPositives(trees1, trees1Train, trees1Val, trees1Test, 1)
printNegatives(trees1, trees1Train, trees1Val, trees1Test, 1)
printPositives(trees2, trees2Train, trees2Val, trees2Test, 2)
printNegatives(trees2, trees2Train, trees2Val, trees2Test, 2)
printPositives(trees3, trees3Train, trees3Val, trees3Test, 3)
printNegatives(trees3, trees3Train, trees3Val, trees3Test, 3)

# 3466 3466 2949 245 272
# 3466 3466 2951 255 260
# 1446 1446 1099 176 171
# 1446 1446 1101 164 181
# 1351 1351 1048 154 149
# 1351 1351 1052 146 153
# 1274 1274 951 170 153
# 1274 1274 999 130 145

def outputTrees(treeList, label):
    trees0Train = treeList[0]
    trees0Val = treeList[1]
    trees0Test = treeList[2]
    load_trees.put_trees("train_orig.txt", [t.asSingleTree() for t in trees0Train])
    load_trees.put_trees("dev_orig.txt", [t.asSingleTree() for t in trees0Val])
    load_trees.put_trees("test_orig.txt", [t.asSingleTree() for t in trees0Test])
    train = []
    for monsantoTree in trees0Train:
        tree = load_trees.clone_tree(monsantoTree.tree)
        if monsantoTree.label == label:
            tree.replace_nodenames("1")
        else:
            tree.replace_nodenames("0")
        train.append(tree)
    load_trees.put_trees("train.txt", train)
    val = []
    for monsantoTree in trees0Val:
        tree = load_trees.clone_tree(monsantoTree.tree)
        if monsantoTree.label == label:
            tree.replace_nodenames("1")
        else:
            tree.replace_nodenames("0")
        val.append(tree)
    load_trees.put_trees("dev.txt", val)
    test = []
    for monsantoTree in trees0Test:
        tree = load_trees.clone_tree(monsantoTree.tree)
        if monsantoTree.label == label:
            tree.replace_nodenames("1")
        else:
            tree.replace_nodenames("0")
        test.append(tree)
    load_trees.put_trees("test.txt", test)


outputTrees([trees0Train, trees0Val, trees0Test], 0)
# zip -m ../data_monsanto/trees/20180418/trees0.zip train_orig.txt dev_orig.txt test_orig.txt train.txt dev.txt test.txt

outputTrees([trees1Train, trees1Val, trees1Test], 1)
# zip -m ../data_monsanto/trees/20180418/trees1.zip train_orig.txt dev_orig.txt test_orig.txt train.txt dev.txt test.txt

outputTrees([trees2Train, trees2Val, trees2Test], 2)
# zip -m ../data_monsanto/trees/20180418/trees2.zip train_orig.txt dev_orig.txt test_orig.txt train.txt dev.txt test.txt

outputTrees([trees3Train, trees3Val, trees3Test], 3)
# zip -m ../data_monsanto/trees/20180418/trees3.zip train_orig.txt dev_orig.txt test_orig.txt train.txt dev.txt test.txt

