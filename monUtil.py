# -*- coding: utf-8 -*-
"""

Created on April 12, 2018

@author:  neerbek
"""

import os
import io
import time
import subprocess
import json


from similarity import load_trees

class StringWrapper:
    def __init__(self):
        self.val = ""

    def append(self, text):
        self.val += text

    def get(self):
        return self.val

class MonsantoTree:
    def __init__(self, tree):
        if tree is None:
            raise Exception("Cannot initialize monTree from empty tree")
        self.index = int(tree.syntax)
        self.monsantoId = tree.word
        self.label = int(tree.right.syntax)
        self.filename = tree.right.word
        self.tree = tree.left

    def asSingleTree(self):
        n = load_trees.Node()
        n.syntax = "{}".format(self.index)
        n.word = self.monsantoId
        self.tree.parent = n
        n.left = self.tree
        nRight = n.add_child()
        nRight.syntax = "{}".format(self.label)
        nRight.word = self.filename
        return n

class MonsantoDocument:
    def __init__(self, count, monsantoId, label):
        self.count = count
        self.monsantoId = monsantoId
        if monsantoId.endswith(","):
            self.monsantoId = monsantoId[:-1]
        self.otherMonsantoIds = []
        self.uri = ""
        self.uriText = ""
        self.text = StringWrapper()
        self.label = label

    def __str__(self):
        return "({}, {}, {})".format(self.count, self.monsantoId, self.uri)

    # static
    def dictToMonsantoDocument(jsonDict):
        expectedVariables = ["count", "monsantoId", "otherMonsantoIds", "uri", "uriText", "text", "label"]
        for e in expectedVariables:
            if e not in jsonDict:
                raise Exception("expected " + e + " in " + str(jsonDict))

        element = MonsantoDocument(int(jsonDict["count"]), jsonDict["monsantoId"], jsonDict["label"])
        element.otherMonsantoIds = jsonDict["otherMonsantoIds"]  # list of strings
        element.uri = jsonDict["uri"]
        element.uriText = jsonDict["uriText"]
        element.text.val = jsonDict["text"]["val"]
        return element

def toJSON(e):
    return json.dumps(e, default=lambda o: vars(o))

def saveJSONList(filename, entries):
    with io.open(filename, 'w', encoding='utf8') as f:
        f.write("[\n")
        for i in range(len(entries)):
            e = entries[i]
            f.write(toJSON(e))
            if i < len(entries) - 1:
                f.write(",\n")
            else:
                f.write("\n")
        f.write("]\n")

def loadJSONList(filename, dictToEntryFunc):
    if not os.path.isfile(filename):
        return []

    lines = []
    with io.open(filename, 'r', encoding='utf8') as f:
        lines = f.readlines()
    jsonlist = json.loads("".join(lines))  # read in as a list of dictionaries
    res = []
    for e in jsonlist:
        res.append(dictToEntryFunc(e))
    return res

def assertTrue(val, msg=None):
    if not val:
        out = "Assertion failed"
        if msg != None:
            out += " " + msg
        raise Exception(out)

def writeFile(sentences, filename, maximum=-1, doLog=True):
    """Writes a list of strings to file, seperates by newline"""
    start = time.time()
    with io.open(filename, 'w+', encoding='utf8') as f:
        for i, s in enumerate(sentences):
            f.write(s + "\n")
            if i == maximum:
                if doLog:
                    print("Maximum reached", i)
                break
            if doLog and i % 2000 == 0:
                print(i, "time elapsed is:", time.time() - start)
    done = time.time()
    if doLog:
        print("File written. Time elapsed is:", done - start)

def runCommand(command):
    if not isinstance(command, list):
        raise Exception("command must be an array")
    if len(command) > 1:
        print("WARN: runCommand take command as an array with one element")
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    # note shell=True is potentially unsafe (security-wise)
    #
    # to check if p is done
    # poll = p.poll()
    # if poll == None:
    #   still runnning...
    #
    # to check returnCode
    # streamdata = p.communicate()[0]
    # rc = p.returncode
    # # must! call communicate and assign returncode (because of theading)
    #
    # to read lines
    # it = iter(p.stdout.readline, b'')
    # for i, line in enumerate(it):
    #   print(line)
    #
    return p

def waitProcess(popen, sleepMillis=50, reportPerMillis=1000):
    start = time.time()
    prev = start
    while True:
        poll = popen.poll()
        if poll == None:
            time.sleep(sleepMillis / 1000)
            cur = time.time()
            if cur - prev > reportPerMillis / 1000:
                print("Waiting on process. Elapsed: {.:2f}".format(cur - start))
        else:
            break

def removeNewline(s):
    # TODO: add support for \n
    return s.replace("\n", " ")

def removeApostrof(s):
    # TODO: add support for "'"
    return s.replace("'", "")  # remove "'" not handled by server_rnn_helper.get_nltk_trees

def removeMultiCommas(s):
    # TODO: is this ok (that we do not support ",,")?
    tmp = s.replace(",,", ",")  # remove multiple commas
    tmp = tmp.replace(", ,", ",")  # remove multiple commas
    while tmp != s:
        s = tmp
        tmp = s.replace(",,", ",")  # remove multiple commas
        tmp = tmp.replace(", ,", ",")  # remove multiple commas
    return s

