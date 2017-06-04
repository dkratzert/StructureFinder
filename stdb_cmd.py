import os
import sys

from searcher import filecrawler

fname = os.path.abspath(sys.argv[1])
filecrawler.put_cifs_in_db(fname)