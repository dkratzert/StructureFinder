import os
import sys

from searcher import filecrawler
from searcher.spinner import Spinner

try:
    fname = os.path.abspath(sys.argv[1])
except IndexError:
    print("No valid search directory given.")
    print("Please run this as 'stdb_rmd [directory]'")
    print("stdb_cmd will search for .cif file in [directory] recoursively.")
else:
    spinner = Spinner()
    spinner.start()
    try:
        filecrawler.put_cifs_in_db(fname)
    except Exception as e:
        print(e)
    spinner.stop()