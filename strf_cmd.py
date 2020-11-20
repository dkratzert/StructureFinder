import argparse
import sys
import time
from pathlib import Path
from sqlite3 import DatabaseError

from misc import update_check
from misc.version import VERSION
from pymatgen.core.lattice import Lattice
from searcher.database_handler import DatabaseRequest, StructureTable
from searcher.filecrawler import put_files_in_db
from searcher.misc import vol_unitcell

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
parser.add_argument("--delete",
                    dest="delete",
                    default=False,
                    action='store_true',
                    help="Delete and do not append to previous database.")
parser.add_argument("-f",
                    dest='cell',
                    #nargs=6,
                    type=lambda s: [float(item) for item in s.split()],
                    help='Search for the specified unit cell.'
                    )


def check_update():
    if update_check.is_update_needed(VERSION=VERSION):
        print('A new Version of StructureFinder is available at '
              'https://www.xs3.uni-freiburg.de/research/structurefinder')


def find_cell(cell: list):
    """
    Searches for unit cells by command line parameters
    """
    cell = [float(x) for x in cell]
    no_result = '\nNo similar unit cell found.'
    if args.outfile:
        dbfilename = args.outfile
    else:
        dbfilename = 'structuredb.sqlite'
    db, structures = get_database(dbfilename)
    # if args.more_results:
    #    # more results:
    #    print('more results on')
    #    vol_threshold = 0.04
    #    ltol = 0.08
    #    atol = 1.8
    # else:
    # regular:
    vol_threshold = 0.02
    ltol = 0.03
    atol = 1.0
    volume = vol_unitcell(*cell)
    # the fist number in the result is the structureid:
    cells = structures.find_by_volume(volume, vol_threshold)
    idlist = []
    if not cells:
        print(no_result)
        sys.exit()
    lattice1 = Lattice.from_parameters(*cell)
    for num, curr_cell in enumerate(cells):
        try:
            lattice2 = Lattice.from_parameters(*curr_cell[1:7])
        except ValueError:
            continue
        mapping = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
        if mapping:
            idlist.append(curr_cell[0])
    if not idlist:
        print(no_result)
        sys.exit()
    else:
        print('\n{} Structures found:'.format(len(idlist)))
        searchresult = structures.get_all_structure_names(idlist)
    print('ID  |      path                                                                |   filename            |   data   ')
    print('-' * 130)
    for res in searchresult:
        Id = res[0]
        path, filename, dataname = [x.decode('utf-8') for x in res if isinstance(x, bytes)]
        print('{:} | {:70s} | {:<25s} | {:s}'.format(Id, path, filename, dataname, ))


def run_index(args=None):
    ncifs = 0
    if not args:
        print('')
    else:
        if not any([args.fillres, args.fillcif]):
            print("Error: You need to give either option -c, -r or both.")
            sys.exit()
        if args.outfile:
            dbfilename = args.outfile
        else:
            dbfilename = 'structuredb.sqlite'
        if args.delete:
            try:
                dbf = Path(dbfilename)
                dbf.unlink()
            except FileNotFoundError:
                pass
            except PermissionError:
                print('Could not acess database file "{}". Is it used elsewhere?'.format(dbfilename))
                print('Giving up...')
                sys.exit()
        db, structures = get_database(dbfilename)
        time1 = time.perf_counter()
        for p in args.dir:
            # the command line version
            lastid = db.get_lastrowid()
            if not lastid:
                lastid = 1
            else:
                lastid += 1
            try:
                ncifs = put_files_in_db(searchpath=p, excludes=args.ex,
                                        structures=structures, lastid=lastid,
                                        fillres=args.fillres, fillcif=args.fillcif)
            except OSError as e:
                print("Unable to collect files:")
                print(e)
            except KeyboardInterrupt:
                sys.exit()
            print("---------------------")
        try:
            if db and structures:
                db.init_textsearch()
                structures.populate_fulltext_search_table()
                structures.make_indexes()
        except TypeError:
            print('No valid files found. They might be in excluded subdirectories.')
        time2 = time.perf_counter()
        diff = time2 - time1
        m, s = divmod(diff, 60)
        h, m = divmod(m, 60)
        tmessage = "\nTotal {3} cif/res files in '{4}'. Duration: {0:>2d} h, {1:>2d} m, {2:>3.2f} s"
        print(tmessage.format(int(h), int(m), s, ncifs, dbfilename))
        check_update()


def get_database(dbfilename):
    db = DatabaseRequest(dbfilename)
    try:
        db.initialize_db()
    except DatabaseError:
        print('Database is corrupt! Delete the file first.')
        sys.exit()
    structures = StructureTable(dbfilename)
    structures.set_database_version(0)  # not an APEX db
    return db, structures


if __name__ == '__main__':
    args = parser.parse_args()
    if args.cell:
        find_cell(args.cell)
    else:
        try:
            if not args.dir:
                parser.print_help()
                check_update()
                sys.exit()
        except IndexError:
            print("No valid search directory given.\n")
            print("Please run this as 'python3 stdb_cmd.py -d [directory]'\n")
            print("stdb_cmd will search for .cif files in [directory] recoursively.")
        run_index(args)
    # find_cell('10.5086  20.9035  20.5072   90.000   94.130   90.000'.split())
