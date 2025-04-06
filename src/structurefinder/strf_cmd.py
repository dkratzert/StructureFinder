import argparse
import sys
import time
from argparse import Namespace
from contextlib import suppress
from pathlib import Path
from sqlite3 import DatabaseError

import gemmi

from structurefinder.misc.update_check import is_update_needed
from structurefinder.misc.version import VERSION
from structurefinder.pymatgen.core.lattice import Lattice
from structurefinder.searcher.crawler2 import find_files, EXCLUDED_NAMES, FileType, Result
from structurefinder.searcher.database_handler import DatabaseRequest, StructureTable
from structurefinder.searcher.filecrawler import fill_db_with_cif_data, fill_db_with_res_data
from structurefinder.searcher.fileparser import CifFile
from structurefinder.searcher.misc import vol_unitcell, regular_results_parameters
from structurefinder.shelxfile.shelx import ShelXFile

DEBUG = False

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
                    help="Merges a database file into the file of '-o' option. Only -o is allowed in addition."
                    )


def check_update():
    if is_update_needed(VERSION=VERSION):
        print('A new Version of StructureFinder is available at '
              'https://dkratzert.de/structurefinder.html')


def find_cell(args: Namespace):
    """
    Searches for unit cells by command line parameters
    """
    no_result = '\nNo similar unit cell found.'
    try:
        cell = [float(x) for x in args.cell]
    except Exception:
        print('No valid cell given. Use space-separated values.')
        sys.exit()
    if args.outfile:
        dbfilename = args.outfile
    else:
        dbfilename = 'structuredb.sqlite'
    db, structures = get_database(dbfilename)
    volume = vol_unitcell(*cell)
    atol, ltol, vol_threshold = regular_results_parameters(volume)
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
        searchresult = structures.get_structure_rows_by_ids(idlist)
    print('ID      |      path                                 '
          '                                    |  filename             |  data name  ')
    print('-' * 130)
    for res in searchresult:
        Id, dataname, filename, size, path = [x.decode('utf-8') if isinstance(x, bytes) else x for x in res]
        # Id, path, filename, dataname
        print(f'{Id:<7} | {path:77s} | {filename:<21s} | {dataname:s}')


def run_index(args=None):
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
                dbf.unlink(missing_ok=True)
            except PermissionError:
                print(f'Could not access database file "{dbfilename}". Is it used elsewhere?')
                print('Giving up...')
                sys.exit()
        db, structures = get_database(dbfilename)
        time1 = time.perf_counter()
        lastid = db.get_lastrowid()
        if not lastid:
            lastid = 1
        else:
            lastid += 1
        for p in args.dir:
            try:
                for num, result in enumerate(find_files(p, exclude_dirs=EXCLUDED_NAMES, progress_callback=None)):
                    if result.file_type == FileType.CIF:
                        process_cif(lastid, result, structures)
                    if result.file_type == FileType.RES:
                        process_res(lastid, result, structures)
                    lastid += 1
            except OSError as e:
                print(f"Unable to collect files: in path '{p}'")
                print(e)
            except KeyboardInterrupt:
                sys.exit()
            print("---------------------")
        finish_database(db, structures)
        time2 = time.perf_counter()
        diff = time2 - time1
        m, s = divmod(diff, 60)
        h, m = divmod(m, 60)
        print(f"\nTotal {len(structures)} cif/res files in '{str(Path(dbfilename).resolve())}'. "
              f"\nDuration: {int(h):>2d} h, {int(m):>2d} m, {s:>3.2f} s")
        import os
        if "PYTEST_CURRENT_TEST" not in os.environ:
            check_update()


def finish_database(db, structures):
    structures.database.commit_db()
    try:
        if db and structures:
            db.init_textsearch()
            db.init_author_search()
            db.populate_fulltext_search_table()
            db.populate_author_fulltext_search()
            db.make_indexes()
    except TypeError:
        print('No valid files found. They might be in excluded subdirectories.')


def process_cif(lastid: int, result: Result, structures: StructureTable) -> bool:
    cif = CifFile()
    cif.cif_data['file_size'] = result.file_size
    cif.cif_data['modification_time'] = result.modification_time
    doc = gemmi.cif.Document()
    try:
        doc.parse_string(result.file_content)
    except ValueError:
        return False
    cif.parsefile(doc)
    if cif.block:
        ok = fill_db_with_cif_data(cif,
                                   filename=result.filename,
                                   path=result.file_path,
                                   structure_id=lastid,
                                   structures=structures)
        if not ok:
            return False
    elif DEBUG:
        print(f'File has no block:', result)
    return True


def process_res(lastid: int, result: Result, structures: StructureTable) -> bool:
    try:
        res = ShelXFile(result.file_path)
    except Exception as e:
        if DEBUG:
            print(e)
            print(f"Could not parse (.res): {result.file_type}")
        return False
    if res:
        with suppress(Exception):
            tst = fill_db_with_res_data(res, result=result, structure_id=lastid, structures=structures)
    if not tst:
        if DEBUG:
            print('res file not added:', result.file_path)
        return False
    return True


def merge_database(args: Namespace):
    argsdict = dict(args.__dict__)
    with suppress(Exception):
        argsdict.pop('outfile')
    with suppress(Exception):
        argsdict.pop('merge')
    if any(argsdict.values()):
        parser.print_help()
        print("\nWarning:\nOnly option '-o' is allowed in combination with '-m'.")
        return
    merge_file_name = Path(args.merge)
    dbfile = Path(args.outfile)
    if not dbfile.exists():
        print(f'Error: Database file {dbfile} not found.')
        return
    if not merge_file_name.exists():
        print(f'Error: Database file {merge_file_name} not found.')
        return
    if not merge_file_name.is_file():
        print(f'{merge_file_name} is not a database file.')
        return
    if not dbfile.is_file():
        print(f'{dbfile} is not a database file.')
    if merge_file_name.samefile(dbfile):
        print('\nCan not merge same file together!\n')
        return
    print(f'Merging {merge_file_name.resolve()} into {dbfile.resolve()}:\n')
    db, structures = get_database(dbfile)
    db.merge_databases(str(merge_file_name))


def get_database(dbfilename):
    db = DatabaseRequest(dbfilename)
    try:
        db.initialize_db()
    except DatabaseError as e:
        print(e)
        print(f'The Database {dbfilename} is corrupt. Unable to open it!')
        sys.exit()
    structures = StructureTable(dbfilename)
    return db, structures


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
    Path('test.sqlite').unlink(missing_ok=True)
    main()
    find_cell(
        Namespace(cell='10.5086  20.9035  20.5072   90.000   94.130   90.000'.split(), outfile='test.sqlite'))
