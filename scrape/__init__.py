"""scrape is a rule-based web crawler and information extraction tool capable of manipulating and merging new and existing documents. XML Path Language (XPath) and regular expressions are used to define rules for filtering content and web traversal. Output may be converted into text, csv, pdf, and/or HTML formats.
"""

import sys


__version__ = '0.9.4'

SYS_VERSION = sys.version_info[0]

# Python 2.x and 3.x compatible builtins
if SYS_VERSION == 2:
    input = raw_input
    range = xrange
