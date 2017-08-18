
import sys
import argparse

import time

from searcher import filecrawler
#from searcher.spinner import Spinner


parser = argparse.ArgumentParser(description='Command line version of StructureFinder to collect cif files to a '
                                             'database.\n'
                                             'StructureFinder will search for cif files in the given directory(s) '
                                             'recursively.')
parser.add_argument("-d",
                    dest="dir",
                    metavar='"directory"',
                    type=str,
                    action='append',
                    help='Directory(s) where cif files are located.')
parser.add_argument("-e",
                    dest="ex",
                    metavar='"directory"',
                    type=str,
                    action='append',
                    help='Directory names to be excluded from the file search. Default is:\n'
                         '"ROOT", ".OLEX", "TMP", "TEMP", "Papierkorb", "Recycle.Bin" '
                         'Modifying -e option discards the default.')
parser.add_argument("-o",
                    dest="outfile",
                    metavar='"file name"',
                    type=str,
                    help='Name of the output database file. Default: "structuredb.sqlite"')


args = parser.parse_args()

try:
    if not args.dir:
        parser.print_help()
        sys.exit()
    fname = args.dir
except IndexError:
    print("No valid search directory given.\n")
    print("Please run this as 'stdb_rmd [directory]'\n")
    print("stdb_cmd will search for .cif files in [directory] recoursively.")
else:
    #spinner = Spinner()
    #spinner.start()
    try:
        time1 = time.clock()
        for p in fname:
            if args.outfile:
                filecrawler.put_cifs_in_db(searchpath=p, dbfilename=args.outfile, excludes=args.ex)
            else:
                filecrawler.put_cifs_in_db(searchpath=p, excludes=args.ex)
        time2 = time.clock()
        diff = time2 - time1
        m, s = divmod(diff, 60)
        h, m = divmod(m, 60)
        tmessage = 'Total time: {0:>2d} h, {1:>2d} m, {2:>3.2f} s'
        print(tmessage.format(int(h), int(m), s))
    except OSError as e:
        print("Unable to collect files:")
        print(e)
    #spinner.stop()
    pass