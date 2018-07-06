
import sys
import argparse

import time

from misc import update_check
from searcher import filecrawler, database_handler

#from searcher.spinner import Spinner
from misc.version import VERSION

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
parser.add_argument("-c",
                    dest="fillcif",
                    default=False,
                    action='store_true',
                    help='Add .cif files (crystallographic information file) to the database.')
parser.add_argument("-r",
                    dest="fillres",
                    default=False,
                    action='store_true',
                    help='Add SHELX .res files to the database.')

args = parser.parse_args()


def check_update():
    if update_check.is_update_needed(VERSION=VERSION):
        print('A new Version of StructureFinder is available at '
              'https://www.xs3.uni-freiburg.de/research/structurefinder')


ncifs = 0
try:
    if not args.dir:
        parser.print_help()
        check_update()
        sys.exit()
except IndexError:
    print("No valid search directory given.\n")
    print("Please run this as 'stdb_rmd [directory]'\n")
    print("stdb_cmd will search for .cif files in [directory] recoursively.")
else:
    if not any([args.fillres, args.fillcif]):
        print("Error: You need to give either option -c, -r or both.")
        sys.exit()
    db = None
    structures = None
    time1 = time.time()
    if args.outfile:
        dbfilename = args.outfile
    else:
        dbfilename = 'structuredb.sqlite'
    for p in args.dir:
        # the command line version
        db = database_handler.DatabaseRequest(dbfilename)
        db.initialize_db()
        lastid = db.get_lastrowid()
        if not lastid:
            lastid = 1
        else:
            lastid += 1
        structures = database_handler.StructureTable(dbfilename)
        try:
            ncifs = filecrawler.put_cifs_in_db(searchpath=p, excludes=args.ex,
                                               structures=structures, lastid=lastid, 
                                               fillres=args.fillres, fillcif=args.fillcif)
        except OSError as e:
            print("Unable to collect files:")
            print(e)
        except KeyboardInterrupt:
            sys.exit()
        print("---------------------")
    if db and structures:
        db.init_textsearch()
        structures.populate_fulltext_search_table()
    time2 = time.time()
    diff = time2 - time1
    m, s = divmod(diff, 60)
    h, m = divmod(m, 60)
    tmessage = "\nTotal {3} cif/res files in '{4}'. Duration: {0:>2d} h, {1:>2d} m, {2:>3.2f} s"
    print(tmessage.format(int(h), int(m), s, ncifs, dbfilename))
    check_update()


