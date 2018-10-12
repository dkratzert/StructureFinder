
import sys
import argparse

import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from misc import update_check
from misc.version import VERSION
from searcher.database_handler import Structure, get_lastrow_id, Base, init_textsearch, populate_fulltext_search_table
from searcher.filecrawler import put_files_in_db

parser = argparse.ArgumentParser(description='Command line version of StructureFinder to collect .cif/.res files to a '
                                             'database.\n'
                                             'StructureFinder will search for cif files in the given directory(s) '
                                             'recursively.  (Either -c, -r or both options must be active!)')
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
    time1 = time.perf_counter()
    if args.outfile:
        dbfilename = args.outfile
    else:
        dbfilename = 'structuredb.sqlite'
    engine = create_engine('sqlite:///' + dbfilename)
    #engine.logging_name = 'log.txt'
    #engine.echo = True
    Base.metadata.create_all(engine)  # creates the table
    Session = sessionmaker(bind=engine)
    session = Session()
    for p in args.dir:
        # the command line version
        # TODO: initialize db here
        lastid = get_lastrow_id(session)
        if not lastid:
            lastid = 1
        else:
            lastid += 1
        try:
            ncifs = put_files_in_db(searchpath=p, excludes=args.ex, engine=engine
                                                session=session, lastid=lastid,
                                                fillres=args.fillres, fillcif=args.fillcif)
        except OSError as e:
            print("Unable to collect files:")
            print(e)
        except KeyboardInterrupt:
            sys.exit()
        print("---------------------")

    session.commit()
    init_textsearch(engine)
    populate_fulltext_search_table(engine)
    time2 = time.perf_counter()
    diff = time2 - time1
    m, s = divmod(diff, 60)
    h, m = divmod(m, 60)
    tmessage = "\nTotal {3} cif/res files in '{4}'. Duration: {0:>2d} h, {1:>2d} m, {2:>3.2f} s"
    print(tmessage.format(int(h), int(m), s, ncifs, dbfilename))
    check_update()


