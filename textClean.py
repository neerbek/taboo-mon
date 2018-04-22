# -*- coding: utf-8 -*-
"""

Created on April 13, 2018

@author:  neerbek
"""
import re

def getFirstWord(s):
    index = s.find(" ")
    if index == -1:
        return s
    return s[:index]

class TextCleaner:
    def __init__(self):
        self.isFirst = True
        self.numbers = set(["{}".format(i) for i in range(10)])

    # line = "HEALY,  CHARLES  E [AG/1000]  [/O=MONSANTO/OU=NA-1000-01/CN=RECIPIENTS/CN=297008] "
    # line = "ian [jan]"
    # self = cleaner
    def cleanLine(self, line):
        line = re.sub(r'[^\x0a-\x7f]', r' ', line)
        line = re.sub(r'[\x0e-\x1f]', r' ', line)
        line.replace("\x0b", " ")
        # for i in range(len(line)):
        #     if line[i] < r'\x1f':
        #         if line[i] not in set([r'\n', r'\r', r'\f']):
        #             line = line[:i] + " " + line[i + 1:]
        line = line.strip()
        if self.isFirst and line == "Message":
            self.isFirst = False
            return ""
        self.isFirst = False
        if line == "-----original  Message-----":
            return ""
        if line.startswith("MONGLY0") and len(line) == len("MONGLY0xxxxxxx"):
            return ""
        if line.startswith("MONGLY") and len(line) == len("MONGLYxxxxxxxx"):
            print("WARN: MONGL id partial pattern2 detected")
            return ""

        if line.startswith("MONGL Y0") and len(line) == len("MONGL Y0xxxxxxx"):
            return ""
        if line.startswith("MONGL Y") and len(line) == len("MONGL Yxxxxxxxx"):
            print("WARN: MONGL id partial pattern detected")
            return ""
        beginnings = line.split(" ")
        beginnings = [b for b in beginnings if len(b) > 0]
        tmp = " ".join(beginnings)
        if tmp == "Confidential - Produced Subject to Protective Order":
            return ""
        line = line.replace("•", "")
        line = line.strip()

        w = getFirstWord(line)
        if w in set(["Sent:", "sent:", "Importance:"]):
            return ""

        if w in set(["From:", "To:", "Subject:", "subject:"]):
            if len(line) == len(w):
                return ""

        if w == "subject:":
            line = "Subject:" + line[len(w):]

        if len(line) == 0:
            return ""

        beginnings = line.split("[")
        if len(beginnings) > 1:
            res = beginnings[0]
            # i = 0
            # e = beginnings[i]
            for e in beginnings[1:]:
                orige = e
                e = e.strip()
                if e.find("]") != -1:
                    esub = e[:e.find("]")]
                    if esub.find(" ") == -1:
                        orige = orige[orige.find("]") + 1:]
                        if len(orige) != 0:  # ow no spaces in stuff in [...] ignoring
                            res += orige
                        continue
                res += "[" + orige
            line = res
        res = ""
        # weird chars
        beginnings = line.split(" ")
        # print("line:", len(beginnings), beginnings, line)
        for e in beginnings:
            orige = e
            e = e.strip()
            if len(e) == 0:
                continue

            if len(e) == 1:
                if e in set(["a", "A", "I", "i", "."]) or e in self.numbers:
                    # print("adding", e)
                    res += " " + e
                continue
            count1 = e.count("~")
            count2 = e.count("=")
            count3 = e.count("--")
            count4 = e.count("'")
            count5 = e.count(".")
            # print(e, count1, count2, count3, count4, count5)
            if count1 + count2 + count3 + count5 > 2:
                continue
            if count4 > 2:
                continue
            if e.find("____") != -1 or e.find("-----") != -1:
                continue
            # print("adding2", e)
            res += " " + e
        # print("res '{}'".format(res))
        return res[1:]

