# -*- coding: utf-8 -*-
"""

Created on April 5, 2018

@author:  neerbek
"""

import math

import tabula
from backends import PDFMinerBackend

import monUtil
import monsantoData

# uri = "../data_monsanto/2018-03-29/50-b-Further-Concern-Over-Surfactant-Absorption-in-the-Gastrointestinal-Tract.pdf"
# uri = "../data_monsanto/2018-03-29/Email-Detailing-Mark%20Martens-Contributions-Developed-Data-to-Gain-EU-Support-Reporting-Roundup-Genotoxicity.pdf"

uri = "../data_monsanto/2018-03-29/monsanto-documents-chart-100917.pdf"
reader = None
with open(uri, "rb") as stream:
    # try:
    reader = PDFMinerBackend(stream)
    # except PDFSyntaxError as e:
    #     raise Exception("Invalid PDF (%s)" % str(e))

metadata = reader.get_metadata()

print(metadata)

refs = reader.get_references()
type(refs)
len(refs)
res = []
seen = set()
for i in range(len(refs)):
    cur = refs[i]
    if cur not in seen:
        res.append(cur)
        seen.add(cur)
links = res
print("unique links:", len(links))

# duplettes
print("removing link 97 for iarc.fr", len(links))
if links[97].ref != "http://monographs.iarc.fr/ENG/Monographs/vol112/mono112-F03.pdf":
    raise Exception("unexpected link found: " + links[97])
print(links[97])
tmp = links[:97]
tmp.extend(links[98:])
links = tmp

print("removing link 118 forbes.com", len(links))
if links[118].ref != "Forbes.com":
    raise Exception("unexpected link found: " + links[118])
tmp = links[:118]
# tmp.extend(links[119:])  # last link
links = tmp

print("unique links2:", len(links))

text = reader.get_text()

# len(text)
# text[:600]

# i = 0
# prev = refs[i]
# while i < len(refs) and prev == refs[i]:
#     i += 1

# print(i, refs[i])

expectedLabels = monsantoData.labels

expectedEmptyNumbers = set([17, 43, 81])

class TableLooper:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.result = []
        self.currentDocument = None
        self.currentCount = None
        self.expectNewDocument = False
        self.expectLongMonId = False
        self.labels = set()
        self.currentLabel = None

    def nextRow(self, row):
        # index = row[0]
        no = row[1]
        bates = row[2]
        title = row[3]
        description = row[4]

        if no == 'No.':
            # print("ignoring title line", index, str(row))
            return

        if isinstance(no, str):
            # print("no is str: " + no)
            no = int(no)

        if math.isnan(no) and not isinstance(bates, str) and not isinstance(title, str):
            if not isinstance(description, str):
                # print("ignoring nan line", index, str(row))
                pass
            else:
                if description in expectedLabels:
                    # print("Found new label: " + description)
                    self.labels.add(description)
                    self.currentLabel = description
                else:
                    if self.currentDocument is None:
                        raise Exception("Got part of description but no current Document")
                    self.currentDocument.text.append(description)
            return

        if not math.isnan(no):
            # new number
            if not (isinstance(bates, str) and (bates.startswith("MONGLY") or bates.startswith("ACQUAVELLAPROD"))):
                if no in expectedEmptyNumbers:
                    bates = "ASSIGNEDID{}".format(no)
                else:
                    print("Got new number but no mon id no = {}, row={}".format(no, row))
                    bates = "N/A"

            if bates.startswith("MONGLY"):
                expectedLength = len("MONGLYxxxxxxxx")
                # if len(bates) > expectedLength:
                #     print("found long id", self.currentCount, bates)
                if len(bates) > expectedLength + 4:
                    print("found long id", self.currentCount, bates)
                    title = bates[expectedLength + 1:] + title   # fix error in extract
                bates = bates[:expectedLength]  # strip extra chars

            if bates == "MONGLY03737014":  # handle known data noise
                # previous document contained two uris but in wrong format, we adjust here
                prev = self.currentDocument
                self.currentDocument = monUtil.MonsantoDocument(self.currentCount, prev.otherMonsantoIds[0], self.currentLabel)
                self.result.append(self.currentDocument)
                prev.otherMonsantoIds = []
                self.currentDocument.uriText = prev.uriText
                self.currentDocument.text.val = prev.text.val

            self.currentCount = int(no)
            self.currentDocument = monUtil.MonsantoDocument(self.currentCount, bates, self.currentLabel)
            self.result.append(self.currentDocument)
            if bates.startswith("ACQUAVELLAPROD") and len(bates) < len("ACQUAVELLAPRODxxxxxxxx"):
                self.expectLongMonId = True

            if self.expectNewDocument:
                raise Exception("got new count while looking for next monid " + str(row))

            if bates == "MONGLY02145917":  # add extra monId to the current document
                for i in range(18, 29 + 1):
                    self.currentDocument.otherMonsantoIds.append("MONGLY021459{}".format(i))
            if bates == "MONGLY00977264":  # add extra monId to the current document
                for i in range(65, 69 + 1):
                    print("adding", i)
                    self.currentDocument.otherMonsantoIds.append("MONGLY009772{}".format(i))
            if bates == "MONGLY01314233":  # add extra monId to the current document
                for i in range(34, 69 + 1):
                    self.currentDocument.otherMonsantoIds.append("MONGLY013142{}".format(i))
            if bates == "MONGLY00878595":  # add extra monId to the current document
                self.currentDocument.otherMonsantoIds.append("MONGLY00878596")
            if bates == "MONGLY05190476":  # add extra monId to the current document
                for i in range(77, 84 + 1):
                    self.currentDocument.otherMonsantoIds.append("MONGLY051904{}".format(i))
            if bates == "MONGLY03549275":  # add extra monId to the current document
                for i in range(76, 79 + 1):
                    self.currentDocument.otherMonsantoIds.append("MONGLY035492{}".format(i))
            if bates == "MONGLY02155826":  # add extra monId to the current document
                for i in range(27, 30 + 1):
                    self.currentDocument.otherMonsantoIds.append("MONGLY021558{}".format(i))
            if bates == "MONGLY01870235":  # add extra monId to the current document
                for i in range(36, 46 + 1):
                    self.currentDocument.otherMonsantoIds.append("MONGLY018702{}".format(i))
            if bates == "MONGLY00987755":  # add extra monId to the current document
                self.currentDocument.otherMonsantoIds.append("MONGLY00987756")
                self.currentDocument.otherMonsantoIds.append("MONGLY00987757")
            if bates == "MONGLY03351983":  # add extra monId to the current document
                self.currentDocument.otherMonsantoIds.append("MONGLY03351984")
            if bates == "MONGLY02054538":  # add extra monId to the current document
                self.currentDocument.otherMonsantoIds.append("MONGLY02054539")
            if bates == "MONGLY03410604":  # add extra monId to the current document
                for i in range(5, 6 + 1):
                    self.currentDocument.otherMonsantoIds.append("MONGLY0341060{}".format(i))

        if math.isnan(no):
            # not new number
            if isinstance(bates, str) and bates.startswith("MONGLY"):
                # extra monid
                if self.expectNewDocument:
                    prev = self.currentDocument
                    self.currentDocument = monUtil.MonsantoDocument(self.currentCount, bates, self.currentLabel)
                    self.currentDocument.text = prev.text  # link by reference
                    self.result.append(self.currentDocument)
                    self.expectNewDocument = False
                else:
                    self.currentDocument.otherMonsantoIds.append(bates)
            if self.expectLongMonId:
                if isinstance(bates, str):
                    tmp = self.currentDocument.monsantoId + bates
                    if len(tmp) != len("ACQUAVELLAPRODxxxxxxxx"):
                        raise Exception("expect lon monsantoId, but got wrong len", str(row))
                    self.currentDocument.monsantoId = tmp
                    self.expectLongMonId = False

        if bates == "AND" or title == "AND":
            # print("found AND", self.currentCount)  # str(row))
            if self.expectNewDocument:
                raise Exception("got bates = 'AND' while looking for next monid " + str(row))
            if len(self.currentDocument.otherMonsantoIds) > 0:
                bates = self.currentDocument.otherMonsantoIds[0]
                self.currentDocument.otherMonsantoIds = self.currentDocument.otherMonsantoIds[1:]
                prev = self.currentDocument
                self.currentDocument = monUtil.MonsantoDocument(self.currentCount, bates, self.currentLabel)
                self.currentDocument.text = prev.text  # link by reference
                self.result.append(self.currentDocument)
                self.expectNewDocument = False
            else:
                self.expectNewDocument = True
            if not math.isnan(no) and not isinstance(title, str) and not isinstance(description, str):
                raise Exception("bates is AND, but there is other contents " + str(row))
            return

        if isinstance(title, str):
            self.currentDocument.uriText += " " + title
        if isinstance(description, str):
            self.currentDocument.text.append(" " + description)


# getting table
df = tabula.read_pdf(uri, pages="all")
# len(df)
# print(df)

looper = TableLooper(df)
for i, row in enumerate(df.itertuples()):
    looper.nextRow(row)

print("texts from pdf", len(looper.result), "- Unique links from pdf", len(links))

if len(looper.result) != len(links):
    raise Exception("expected same number of links and rows")
count = len(looper.result)

# setting the urls
for i in range(count):
    looper.result[i].uri = links[i].ref

# for i in range(count):
#     print(i, " - Count", looper.result[i].count, " - MonID", looper.result[i].monsantoId, " - link:", links[i])

# for i in range(count):
#     if len(looper.result[i].text.val) == 0:
#         print(i, " - Count", looper.result[i].count, " - MonID", looper.result[i].monsantoId, " - link:", links[i], " - uri text", looper.result[i].uriText)

# has no text value
# i = 79
# print(i, " - Count", looper.result[i].count, " - MonID", looper.result[i].monsantoId, " - link:", links[i], " - text", looper.result[i].text.val)

# show we got the otherMonsantoIds
# for i in range(count):
#     if len(looper.result[i].otherMonsantoIds) > 0:
#         print(i, " - Count", looper.result[i].count, " - MonID", looper.result[i].monsantoId)
#         for j in range(len(looper.result[i].otherMonsantoIds)):
#             print(i, " - Count", looper.result[i].count, " - OtherMonID", looper.result[i].otherMonsantoIds[j])

i = 21
print(i, " - Count", looper.result[i].count, " - MonID", looper.result[i].monsantoId, " - link:", links[i], " - uri text", looper.result[i].uriText, " - desc", looper.result[i].text.val)
dir(looper.result[i])
dir(looper.result[i].text)


count = len(looper.result)
labels = {}
for i in range(count):
    if looper.result[i].label not in labels.keys():
        labels[looper.result[i].label] = 0
    labels[looper.result[i].label] += 1
print(labels)

count = len(looper.result)
labels = {}
added = 0
for i in range(count):
    if looper.result[i].label not in labels.keys():
        labels[looper.result[i].label] = 0
    labels[looper.result[i].label] += len(looper.result[i].otherMonsantoIds)
    if looper.result[i].monsantoId not in looper.result[i].otherMonsantoIds:
        labels[looper.result[i].label] += 1
        added += 1
print(labels)
print(added)

filename = "monsantoLabelEntries.json"
monUtil.saveJSONList(filename, looper.result)

tmp = monUtil.loadJSONList(filename, monUtil.MonsantoDocument.dictToMonsantoDocument)

len(tmp)
len(links)

filename2 = "monsantoLabelEntries2.json"
monUtil.saveJSONList(filename2, tmp)
# diff monsantoLabelEntries.json monsantoLabelEntries2.json
# (no diff) success!


