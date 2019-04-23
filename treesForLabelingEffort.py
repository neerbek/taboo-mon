# -*- coding: utf-8 -*-
"""

Created on April 23, 2019

@author:  neerbek
"""

# uses trees generated by reorderTreesToOriginal.py

import os
import random
import projectSetup  # noqa: F401
from similarity import load_trees

dataDir = os.path.join(os.getenv("HOME"), "jan/ProjectsData/phd/DLP/Monsanto/data/trees/20180418")

trees0 = load_trees.get_trees(os.path.join(dataDir, "trees0", "trees0_all_sorted_orig.txt"))
trees1 = load_trees.get_trees(os.path.join(dataDir, "trees1", "trees1_all_sorted_orig.txt"))
trees2 = load_trees.get_trees(os.path.join(dataDir, "trees2", "trees2_all_sorted_orig.txt"))
trees3 = load_trees.get_trees(os.path.join(dataDir, "trees3", "trees3_all_sorted_orig.txt"))

trees = [trees0, trees1, trees2, trees3]
resList = [{}, {}, {}, {}]   # dict from monId to list of sentence (trees)
for j, treeList in enumerate(trees):
    res = resList[j]
    for i, t in enumerate(treeList):
        monId = t.word
        docIndex = t.syntax
        n = t.right
        docTitle = n.word
        docLabel = n.syntax
        if monId not in res:
            res[monId] = []
        if len(res[monId]) > 0:
            prevTree = res[monId][-1]
            if prevTree.word != monId:
                raise Exception("monId ordering mismatch {} {}".format(i, monId))
            if int(prevTree.syntax) >= int(docIndex):
                print(prevTree.syntax, docIndex)
                raise Exception("docIndex ordering mismatch {} {}".format(i, monId))
            if prevTree.right.syntax != docLabel:
                raise Exception("doc has two labels {} {}".format(i, monId))
        res[monId].append(t)

print("Documents 0 {}, 1 {}, 2 {}, 3 {}".format(len(resList[0]), len(resList[1]), len(resList[2]), len(resList[3])))

threshold = 100
removed = [0, 0, 0, 0]  # counts of number of documents removed
shortDocs = [[], [], [], []]  # list of all sentences from docs with less than 100 sentences
for i, res in enumerate(resList):
    monIds = list(res.keys())
    monIds = sorted(monIds)   # ascending order, every run will generate same ordering
    for monId in monIds:
        if len(res[monId]) > threshold:
            removed[i] += 1
        else:
            shortDocs[i].extend(res[monId])

print("Removed: 0 {}, 1 {}, 2 {}, 3 {}".format(removed[0], removed[1], removed[2], removed[3]))
print("Sizes: 0 {}, 1 {}, 2 {}, 3 {}".format(len(shortDocs[0]), len(shortDocs[1]), len(shortDocs[2]), len(shortDocs[3])))
# Removed: 0 6, 1 3, 2 3, 3 3

random.seed(37279)
samples = [[], [], [], []]
sampleSize = 250
for i, docs in enumerate(shortDocs):
    samples[i] = random.sample(docs, sampleSize)

res = []
for i, sample in enumerate(samples):
    res.extend(sample)
len(res)
load_trees.put_trees(os.path.join(dataDir, "sample_250_4_labels.txt"), res)

