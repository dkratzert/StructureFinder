import os
import sys
import argparse

from searcher import filecrawler
#from searcher.spinner import Spinner


parser = argparse.ArgumentParser(description='Command line version of StructureFinder to collect cif files.\n'
                                             'StructureFinder will search for cif files in the given directory '
                                             'recursively.')
parser.add_argument("-d", dest="dir", metavar='"directory"',
                    #nargs='+',
                    action='append',
                    help='directory(s) where cif files are located.')

args = parser.parse_args()

try:
    #fname = os.path.abspath(sys.argv[1])
    if not args.dir:
        parser.print_help()
    #print(args)
    fname = args.dir
except IndexError:
    print("No valid search directory given.\n")
    print("Please run this as 'stdb_rmd [directory]'\n")
    print("stdb_cmd will search for .cif files in [directory] recoursively.")
else:
    #spinner = Spinner()
    #spinner.start()
    #try:
    for p in fname:
        filecrawler.put_cifs_in_db(searchpath=p)
    #except Exception as e:
    #    print(e)
    #spinner.stop()
    pass