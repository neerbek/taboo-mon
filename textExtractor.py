# -*- coding: utf-8 -*-
"""

Created on April 12, 2018

@author:  neerbek
"""

import os
# import re
from importlib import reload
import html
from urllib import parse

import monUtil
import monsantoData

# from backends import PDFMinerBackend
reload(monUtil)
datadir = "../data_monsanto/2018-04-12"
decryptdir = "../data_monsanto/2018-04-12-workdir"
filename = "monsantoLabelEntries.json"

labels = monUtil.loadJSONList(filename, monUtil.MonsantoDocument.dictToMonsantoDocument)

def getBasename(monsantoDocument):
    url = monsantoDocument.uri
    name = url[url.rindex("/") + 1:]
    return name

def printOutput(popen):
    it = iter(popen.stdout.readline, b'')
    for line in it:
        print(line.decode("utf-8"), end='')

filenames = []
count = len(labels)
for i in range(count):
    url = labels[i].uri
    name = url[url.rindex("/") + 1:]
    # name = os.path.join(datadir, name)
    filenames.append(name)

# PDFMinerBackend fails on these documents we will run from command line instead


# qpdf --password="" --decrypt ../data_monsanto/2018-03-29/16-Internal-Email-Showing-Dr-Healy-Asked-Colleagues-to-Review-Study-That-Found-Roundup-and-Glyphosate-Adverse-Effects.pdf 1.pdf
# pdf2txt 1.pdf 
#
i = 0
for i in range(count):
    filename = html.unescape(filenames[i])   # convert html entities (&amp;)
    filename = parse.unquote_plus(filename)  # convert url encoding (%20)
    filename = filename.replace("$", "\\$")
    filename = filename.replace(" ", "\\ ")
    # filename = re.escape(filename)  # escape $ and space. Also puts a \ in front of - and . (this does not seem to be hurtful)

    if filename == "46-b-TNO-Study-on-Dermal-Absorption-Referenced-in-Email.pdf":
        print("replacing filename")
        filename = "46-b-Monsanto-Executive-Roundup-Dermal-Absorption-Studies-Could-Blow-Roundup-Risk-Evaluations.pdf"
    if filename == "52-a-Monsanto-Aware-of-Dermal-Penetration-Studies-Showing-Formulated-Roundup-is-Absorbed-at-Higher-Rate-and-is-More-Toxic.pdf":
        filename = "73-a-Monsanto-Aware-of-Dermal-Penetration-Studies-Showing-Formulated-Roundup-is-Absorbed-at-Higher-Rate-and-is-More-Toxic.pdf"
    if filename == "52-c-Monsanto-Fact-Sheet-on-Ethylene-Glycol-Humectant-Found-in-Most-Roundup-Formulations-is-Listed-on-California-Prop-65-List-of-Reproductive-Toxicants.pdf":
        filename = "73-c-Monsanto-Fact-Sheet-on-Ethylene-Glycol-Humectant-Found-in-Most-Roundup-Formulations-is-Listed-on-California-Prop-65-List-of-Reproductive-Toxicants.pdf"
    if filename == "50-a-Monsanto-Scientist-Due-to-Higher-Rate-of-Glyphosate-Absorption-Monsanto-Cannot-Justify-Avoiding-Toxicity-Testing.pdf":
        filename = "75-a-Monsanto-Scientist-Due-to-Higher-Rate-of-Glyphosate-Absorption-Monsanto-Cannot-Justify\ Avoiding-Toxicity-Testing-with-Similar-Inert-Ingrediants.pdf"
    if filename == "50-b-Further-Concern-Over-Surfactant-Absorption-in-the-Gastrointestinal-Tract.pdf":
        filename = "75-b-Further-Concern-Over-Surfactant-Absorption-in-the-Gastrointestinal-Tract.pdf"
    labels[i].uri = filename
    efile = os.path.join(datadir, filename)
    dfile = os.path.join(decryptdir, filename)
    cmd = ['qpdf', '--password=\"\"', '--decrypt', efile, dfile]
    cmd = [" ".join(cmd)]
    popen = monUtil.runCommand(cmd)
    monUtil.waitProcess(popen, reportPerMillis=500)
    # popen.communicate()
    rc = popen.returncode
    if rc != 0:
        print("ERROR: failed to decode " + filename)
        print(labels[i])
        printOutput(popen)
        break
    if i % 10 == 0:
        print("processed {}/{}".format(i, count))


filename = "monsantoDataEntries.json"
monUtil.saveJSONList(filename, labels)

labels = monUtil.loadJSONList(filename, monUtil.MonsantoDocument.dictToMonsantoDocument)
filename2 = "monsantoDataEntries2.json"
monUtil.saveJSONList(filename2, labels)
# diff monsantoDataEntries.json monsantoDataEntries2.json == None => success

for i in range(count):
    filename = labels[i].uri
    efile = os.path.join(datadir, filename)
    dfile = os.path.join(decryptdir, filename)
    cmd = ['qpdf', '--password=\"\"', '--decrypt', efile, dfile]
    cmd = [" ".join(cmd)]
    popen = monUtil.runCommand(cmd)
    monUtil.waitProcess(popen, reportPerMillis=500)
    # popen.communicate()
    rc = popen.returncode
    if rc != 0:
        print("ERROR: failed to decode " + filename)
        print(labels[i])
        printOutput(popen)
        break
    if i % 10 == 0:
        print("processed {}/{}".format(i, count))

# labelList = [label for label in iter(monsantoData.labels)]
# class1 = [e for e in labels if e.label == labelList[0]]
# class2 = [e for e in labels if e.label == labelList[1]]
# class3 = [e for e in labels if e.label == labelList[2]]
# class4 = [e for e in labels if e.label == labelList[3]]
# print(len(class1), len(class2), len(class3), len(class4))

i = 0
for i in range(count):
    filename = labels[i].uri
    pdffile = os.path.join(decryptdir, filename)
    txtfile = pdffile[:-4] + ".txt"
    cmd = ['pdf2txt', pdffile, '>', txtfile]
    cmd = [" ".join(cmd)]
    popen = monUtil.runCommand(cmd)
    printOutput(popen)
    monUtil.waitProcess(popen, reportPerMillis=500)
    # popen.communicate()
    rc = popen.returncode
    if rc != 0:
        print("ERROR: failed to decode " + filename)
        print(labels[i])
        printOutput(popen)
        break
    if i % 10 == 0:
        print("processed {}/{}".format(i, count))

# see ../notes.txt for known extraction problems (2 documents are scanned without ocr)
