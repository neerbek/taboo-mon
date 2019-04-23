# -*- coding: utf-8 -*-
"""

Created on March 23, 2019

@author:  neerbek
"""

import os
# need taboo-core in pythonpath
import projectSetup  # noqa: F401
from similarity import load_trees

label = '3'
treeName = 'trees3'

dataDir = os.path.join(os.getenv("HOME"), "jan/ProjectsData/phd/DLP/Monsanto/data/trees/20180418")
t1 = load_trees.get_trees(os.path.join(dataDir, treeName, "train_orig.txt"))
t2 = load_trees.get_trees(os.path.join(dataDir, treeName, "dev_orig.txt"))
t3 = load_trees.get_trees(os.path.join(dataDir, treeName, "test_orig.txt"))

trees = []
trees.extend(t1)
trees.extend(t2)
trees.extend(t3)
len(trees), len(t1), len(t2), len(t3)

res = []
for t in trees:
    monId = t.word
    docIndex = t.syntax
    n = t.right
    docTitle = n.word
    docLabel = n.syntax
    if docLabel == label:
        res.append(t)

len(res)


def documentSortKey(t):
    monId = t.word
    docIndex = t.syntax
    index = 1000000 + int(docIndex)
    return monId + "_" + str(index)


sortedRes = sorted(res, key=documentSortKey)

monIdSeen = set()
prevId = None
prevIndex = None
for t in sortedRes:
    monId = t.word
    docIndex = int(t.syntax)
    if prevId != monId:
        if monId in monIdSeen:
            raise Exception("Id seen twice: " + monId)
        monIdSeen.add(monId)
        prevId = monId
        prevIndex = docIndex
    else:
        if prevIndex >= docIndex:
            raise Exception("For id " + monId + " new index " + str(docIndex) + " comes after " + str(prevIndex))
        prevIndex = docIndex
print("Done")

# for i in range(0, 10):
#      print(sortedRes[i].right)

load_trees.put_trees(os.path.join(dataDir, treeName, "all_sorted_orig2.txt"), sortedRes)
