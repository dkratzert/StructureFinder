import os
import sys

from searcher import filecrawler
#from searcher.spinner import Spinner

try:
    fname = os.path.abspath(sys.argv[1])
except IndexError:
    print("No valid search directory given.\n")
    print("Please run this as 'stdb_rmd [directory]'\n")
    print("stdb_cmd will search for .cif files in [directory] recoursively.")
else:
    #spinner = Spinner()
    #spinner.start()
    #try:
    filecrawler.put_cifs_in_db(searchpath=fname)
    #except Exception as e:
    #    print(e)
    #spinner.stop()