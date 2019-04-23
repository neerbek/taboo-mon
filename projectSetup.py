# -*- coding: utf-8 -*-
"""

Created on March 23, 2019

@author:  neerbek
"""

# for loading dependencies - your paths may vary

import os
import sys

# (setenv "PYTHONPATH" (concat (getenv "PYTHONPATH") ":" (getenv "HOME") "/jan/taboo/taboo-core"))

importdirs = [
    os.path.join(os.getenv("HOME"), "jan/taboo/taboo-core")
]

for f in importdirs:
    if f not in sys.path:
        print("adding", f, "to path")
        sys.path.append(f)
