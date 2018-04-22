# -*- coding: utf-8 -*-
"""

Created on April 13, 2018

@author:  neerbek
"""

import unittest

import tests.RunTimer  # from taboo-core
import textClean

class TestTextCleaner(unittest.TestCase):
    def setUp(self):
        self.timer = tests.RunTimer.Timer()

    def tearDown(self):
        self.timer.report(self, __file__)

    def test_textCleaner(self):
        cleaner = textClean.TextCleaner()
        sent = "From:"
        res = cleaner.cleanLine(sent)
        self.assertEqual("", res)
        sent = "From: JAN"
        res = cleaner.cleanLine(sent)
        self.assertEqual("From: JAN", res)
        sent = "subject: JAN"
        res = cleaner.cleanLine(sent)
        self.assertEqual("Subject: JAN", res)

    def test_squareParentheses(self):
        cleaner = textClean.TextCleaner()
        sent = "[jan]"
        res = cleaner.cleanLine(sent)
        self.assertEqual("", res)
        sent = "ian [jan]"
        res = cleaner.cleanLine(sent)
        self.assertEqual("ian", res)
        sent = "[jan] ian"
        res = cleaner.cleanLine(sent)
        self.assertEqual("ian", res)
        sent = "ian1[jan] ian2"
        res = cleaner.cleanLine(sent)
        self.assertEqual("ian1 ian2", res)
        sent = "ian1[jan] [42]ian2[43]"
        res = cleaner.cleanLine(sent)
        self.assertEqual("ian1 ian2", res)
        sent = "ian1[jan] [4 2]ian2[43]"
        res = cleaner.cleanLine(sent)
        self.assertEqual("ian1 [4 2]ian2", res)
        sent = "ian1[jan] [ian2[43]"
        res = cleaner.cleanLine(sent)
        self.assertEqual("ian1 [ian2", res)
        sent = "ian1[jan] [ian2[43]]"
        res = cleaner.cleanLine(sent)
        self.assertEqual("ian1 [ian2]", res)

    def test_monglyId(self):
        cleaner = textClean.TextCleaner()
        sent = "MONGL Y02286843"
        res = cleaner.cleanLine(sent)
        self.assertEqual("", res)
        sent = "MONGL Y0228684"
        res = cleaner.cleanLine(sent)
        self.assertEqual(sent, res)
        sent = "MONGLY0xxxxxxx"
        res = cleaner.cleanLine(sent)
        self.assertEqual("", res)

    def test_weirdDots(self):
        cleaner = textClean.TextCleaner()
        sent = "MONGL • • • • • • • • • • • •"
        res = cleaner.cleanLine(sent)
        self.assertEqual("MONGL", res)

    def test_weirdChars(self):
        cleaner = textClean.TextCleaner()
        sent = "jan1 l ... gl~Y=P~h~os~-a=t=e\"-!) jan2 c-'Ca'--'n-\"d-'-itc.cs-'a=-c'-\"ti-'-v-'-e-'-in~g\"'r_ce...cdc.cie-'-nc.ct'-, g\"'l_,_y\"-p-'-ho-'-s'--'a\"-'t-'-e,_, w'--'-'-e-'--re'--'-'-sh-'-o-'-w~n_cto-'--\"in-'-'d\"-'u-'-'c_ce_.p'--'r-'-o-\"-lif'--'e-'--ra=-t=-io'--'n-'---'--of=-M_c__cCcc.F_--'--7-'c'--'e-\"ll-'-s'--. T-'--h'-\"i-'-s ____ -----i jan3"
        res = cleaner.cleanLine(sent)
        self.assertEqual("jan1 jan2 jan3", res)

    def test_singleChars(self):
        cleaner = textClean.TextCleaner()
        sent = "I"
        res = cleaner.cleanLine(sent)
        self.assertEqual(sent, res)
        sent = "."
        res = cleaner.cleanLine(sent)
        self.assertEqual(sent, res)
        sent = ".\n"
        res = cleaner.cleanLine(sent)
        self.assertEqual(".", res)
        sent = ".\xb7\n"
        res = cleaner.cleanLine(sent)
        self.assertEqual(".", res)
        sent = "4"
        res = cleaner.cleanLine(sent)
        self.assertEqual(sent, res)
        sent = "z"
        res = cleaner.cleanLine(sent)
        self.assertEqual("", res)
        sent = "b"
        res = cleaner.cleanLine(sent)
        self.assertEqual("", res)


n1 = "~re~c~e~n\"'\"t\"'\"jn~vi,;,;,t~\"\"o\"\"'h,;,.;u\"'\"m\"\"a\"\"n~d\"\"e;..rm~a;..I a\"\"b\"\"'s\"\"'o\"'\"r,;;.pt\"'\"io\"\"n\"\"\"\"\"s\"'tu,;,.;d\"\"ie\"\"'s\"'\"\"\"h\"'av\"'\"e'-\"\"b\"\"e.;;.e\"\"n\"\"\"c\"\"o\"\"n\"\"d.;;,uc\"\"t\"\"e\"\"d-'o;.,;,n.;...;,,gl'\"\"y\"'p\"\"h\"\"os\"\"'a\"'\"t\"\"e-'o;.,;,r..,g\"\"ly,.,p\"\"h\"'o\"\"s\"'a\"\"te\"\"--'b'\"\"a\"'s\"\"'e\"\"d'----_____ ---(  Formatted:  Font:  Italic"

n2 = "... sk~i ... n ... a~n~d ... t~h ... e ... t ... o~P ... e ... tr ... a ... tu ... m~c ... o ... m ... e ... u ... m~la ... y._e ... r ... s ... w ... h ... i ... ch ...... w ... o ... u ... ld ...... b ... e ... c ... o ... n ... s ... id ... e ... re ... d ...... e ... xf ... o ... li ... a ... te ... d ... o ... v ... e ... r ... t ... im ... e ... :._a .. n ... d...._(i .. ii)._t ... e ... s ... t ... ce ... I ... ls.__ _________ l Formatted:  Font:  Italic"

n3 = "_ _.----{"

n4 = "~ - - - - - - - - - - - - - - - - - -~\
______"

n5 = " ___ ~------{ Formatted:  Highlight\
------1"

n6 = "(of--which--glyphosate-Goo-tai1-1ing--herhlGici-es--ar-e-,H1ly.-a--small(cid:173)\
portion)"

n7 = "-  -\
-----7"

n8 = "-  -"

n9 = "_____  Comment : r would ,aypo,siblerecall bias."

# n10
# ------j (amment : frobably uO<Jd lo be
# ' \   j  cou,iot<Jut  ... glyphosale or glyphosate acid or
# j  glyphosetotechnicalgrede ... or maybe best M check
# ! repmts/pub1icetio<1 at1d use whet the authors used
# j (amment : Table, 3·8 @l presented
# \'·················································································


# split sentences:
# <index: 457, sentence: Thanks,
# chuck
# [mail to
# To: HEALY, CHARLES
# Subject: Manuscript CBT0548 for review
# Dear Dr Charles Healy,
# on Behalf of cell Biology and Toxicology
# In view of your expertise I would be very grateful if you could review the following manuscript which has
# been submitted to cell Biology and Toxicology. >
# <index: 755, sentence: Manuscript Number: CBT0548
# Title: cytotoxicity of herbicide Roundup and its active ingredient, glyphosate in rats
# Abstract: Glyphosate is the active ingredient and polyoxyethyleneamine, the major component, is the
# surfactant present in the herbicide Roundup formulation. >
# <index: 2755, sentence: In case you are interested in reviewing this submission please click on this link:
# http://cbto.edmgr.com/l
# If you do not have time to do this, or do not feel qualified, please click on this link:
# http://cbto.edmgr.com/l
# we hope you are willing to review the manuscript. >


#
# __ __ comment -LSB- wh17J; JOHN IS WRONG- IT IS THERE IT IS THE 3 ONE MENTIONED BY HILL 1 Comment Strong 
# in Hill article refers i I I to the size of the difference between exposure I groups, not presenoelabsenc
# e of statistical I_ significance_,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# , -RRB- 2_ The association is not consistent, since four out of five mouse studies did not similar renal 
# neoplasms at comparable doses_ 3_ The association is not specific,, since females of this pivotal study, 
# which have been exposed to higher levels of glyphosate did not develop renal neoplasms_ Also, there were 
# no renal findings in the LO group, whereas the control group had two_ Comment This is not what Hill meant
#  I by specificity.


if __name__ == "__main__":
    unittest.main()
