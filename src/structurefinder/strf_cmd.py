import argparse
import sys
import time
from argparse import Namespace
from pathlib import Path

from structurefinder.db.database import DB
from structurefinder.misc.update_check import is_update_needed
from structurefinder.misc.version import VERSION
from structurefinder.searcher.filecrawler import excluded_names
from structurefinder.searcher.worker import Worker

parser = argparse.ArgumentParser(
    description=f'Command line version {VERSION} of StructureFinder to collect .cif/.res files to a '
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
                    metavar='"sqlite file name"',
                    type=str,
                    help='Name of the output database file. Default: "./structuredb.sqlite"\n'
                         'Also used for the commandline search (-f option).')
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
parser.add_argument("--delete",
                    dest="delete",
                    default=False,
                    action='store_true',
                    help="Delete and do not append to previous database.")
parser.add_argument("-f",
                    dest='cell',
                    # nargs=6,
                    metavar='"unit cell"',
                    type=lambda s: [float(item) for item in s.split()],
                    help='Search for the specified unit cell. \n'
                         'The cell values have to be enclosed in brackets.'
                    )
parser.add_argument("-m",
                    dest='merge',
                    metavar='"sqlite file name"',
                    default=False,
                    type=str,
                    help="Merges a database file into the file of '-o' option."
                    )


def check_update():
    if is_update_needed(VERSION=VERSION):
        print('A new Version of StructureFinder is available at '
              'https://dkratzert.de/structurefinder.html')


def find_cell(args: Namespace):
    """
    Searches for unit cells by command line parameters
    """
    try:
        cell = [float(x) for x in args.cell]
    except Exception:
        print('No valid cell given. Use space-separated values.')
        sys.exit()
    if args.outfile:
        dbfilename = args.outfile
    else:
        dbfilename = 'structuredb.sqlite'
    db = DB()
    db.load_database(Path(dbfilename))
    searchresult = db.search_cell(cell)
    if not searchresult:
        print('\nNo similar unit cell found.')
        sys.exit()
    print('ID      |      path                                 '
          '                                    |  filename             |  data name  ')
    print('-' * 130)
    for res in searchresult:
        print(f'{res.Id:<7} | {res.path.decode():77s} | {res.filename.decode():<21s} | {res.dataname.decode():s}')



def run_index(args=None):
    if not args:
        print('')
    else:
        if not any([args.fillres, args.fillcif]):
            print("Error: You need to give either option -c, -r or both.")
            sys.exit()
        if args.outfile:
            dbfilename: str = args.outfile
        else:
            dbfilename = 'structuredb.sqlite'
        if args.delete:
            try:
                dbf = Path(dbfilename)
                dbf.unlink()
            except FileNotFoundError:
                pass
            except PermissionError:
                print(f'Could not acess database file "{dbfilename}". Is it used elsewhere?')
                print('Giving up...')
                sys.exit()
        db = DB()
        db.load_database(Path(dbfilename))
        time1 = time.perf_counter()

        with db.Session(autoflush=False) as session:
            db.session = session
            for p in args.dir:
                # the command line version
                lastid = db.get_lastrowid()
                if not lastid:
                    lastid = 1
                else:
                    lastid += 1
                try:
                    _ = Worker(searchpath=p, add_res_files=args.fillres, add_cif_files=args.fillcif, lastid=lastid,
                               db=db, excludes=args.ex if args.ex else excluded_names, standalone=True)
                except OSError as e:
                    print("Unable to collect files:")
                    print(e)
                    raise
                except KeyboardInterrupt:
                    sys.exit()
                print("---------------------")
            db.init_textsearch()
            db.init_author_search()
            db.populate_fulltext_search_table()
            db.populate_author_fulltext_search()
            # TODO: make indexes work:
            # db.make_indexes()
            session.flush()
            session.commit()
        # print('No valid files found. They might be in excluded subdirectories.')
        time2 = time.perf_counter()
        diff = time2 - time1
        m, s = divmod(diff, 60)
        h, m = divmod(m, 60)
        print(f"\nTotal {len(db)} cif/res files in '{str(Path(dbfilename).resolve())}'. "
              f"\nDuration: {int(h):>2d} h, {int(m):>2d} m, {s:>3.2f} s")
        import os
        if "PYTEST_CURRENT_TEST" not in os.environ:
            check_update()


def merge_database(args: Namespace):
    merge_file_name = args.merge
    dbfile = args.outfile
    if not merge_file_name or not Path(merge_file_name).is_file():
        return
    if Path(merge_file_name).samefile(dbfile):
        print('\nCan not merge same file together!\n')
        return
    db = DB()
    db.merge_databases(merge_file_name)


def main():
    args = parser.parse_args()
    if args.cell:
        find_cell(args)
    elif args.merge:
        merge_database(args)
    else:
        if not args.dir:
            parser.print_help()
            print("\n --> No valid search directory given.\n")
            sys.exit()
        run_index(args)


if __name__ == '__main__':
    main()
    # find_cell('10.5086  20.9035  20.5072   90.000   94.130   90.000'.split())
