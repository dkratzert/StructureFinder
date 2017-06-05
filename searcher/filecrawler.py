"""
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <daniel.kratzert@uni-freiburg.de> wrote this file. As long as you retain this 
* notice you can do whatever you want with this stuff. If we meet some day, and 
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: daniel
"""
import os
import fnmatch as fn
import sys
from pathlib import Path
from pprint import pprint

import time
from searcher.database_handler import StructureTable, DatabaseRequest
from searcher.fileparser import Cif
from searcher.spinner import Spinner


def create_file_list(searchpath='None', endings='cif'):
    """
    walks through the file system and collects cells from res/cif files
    into a database
    """
    if not os.path.isdir(searchpath):
        print('search path {0} not found! Or no directory!'.format(searchpath))
        sys.exit()
    print('collecting files...')
    res = filewalker(searchpath)
    print('ready')
    return res


def filewalker(startdir, endings="*.cif"):
    """
    file walker with pathlib
    :param startdir: 
    :param endings: 
    :return:
     
    #>>> filewalker('../')
    """
    p = Path(startdir)
    paths = p.rglob("*.cif")
    return paths


def filewalker_walk(startdir, endings, add_excludes=[]):
    """
    walks through the filesystem starting from startdir and searches
    for files with ending endings.
    """
    filelist = []
    excludes = ['.olex', 'dsrsaves']
    if add_excludes:
        excludes.extend(add_excludes)
    print('collecting files below ' + startdir)
    for root, dirs, files in os.walk(startdir):  # @UnusedVariable
        for num, filen in enumerate(files):
            if fn.fnmatch(filen, '*.{0}'.format(endings)):
                if os.stat(os.path.join(root, filen)).st_size == 0:
                    continue
                filelist.append([os.path.join(root, filen), filen])
            else:
                continue
    return filelist


def put_cifs_in_db(searchpath):
    dbfilename = "structuredb.sqlite"
    db = DatabaseRequest(dbfilename)
    db.initialize_db()
    structures = StructureTable(dbfilename)
    n = 1
    spinner = Spinner()
    spinner.start()
    time1 = time.clock()
    for filepth in create_file_list(str(searchpath), endings='cif'):
        if not filepth.is_file():
            continue
        filename = filepth.name
        path = str(filepth.parents[0])
        structure_id = n
        cif = Cif(filepth)
        if not cif.ok:
            continue
        if cif and filename and path:
            fill_db_tables(cif, filename, path, structure_id, structures)
            n += 1
        if n % 300 == 0:
            structures.database.commit_db()
    time2 = time.clock()
    diff = time2 - time1
    spinner.stop()
    print('\nAdded {} cif files to database in: {} s'.format(n, round(diff, 2)))
    structures.database.commit_db("Committed")


def fill_db_tables(cif, filename, path, structure_id, structures):
    """
    Fill all info from cif file into the database tables 
    :param structures: structures database object
    :param cif: 
    :param filename: 
    :param path: 
    :param structure_id: 
    :return: 
    """
    a = cif._cell_length_a
    b = cif._cell_length_b
    c = cif._cell_length_c
    alpha = cif._cell_angle_alpha
    beta = cif._cell_angle_beta
    gamma = cif._cell_angle_gamma
    measurement_id = structures.fill_measuremnts_table(filename, structure_id)
    structures.fill_structures_table(path, filename, structure_id, measurement_id, cif.cif_data['data'])
    structures.fill_cell_table(structure_id, a, b, c, alpha, beta, gamma)
    #pprint(cif._atom)
    for x in cif._atom:
        try:
            structures.fill_atoms_table(structure_id, x,
                                         cif._atom[x]['_atom_site_type_symbol'],
                                         cif._atom[x]['_atom_site_fract_x'].split('(')[0],
                                         cif._atom[x]['_atom_site_fract_y'].split('(')[0],
                                         cif._atom[x]['_atom_site_fract_z'].split('(')[0])
        except KeyError as e:
            pass
            #print("Atom:", x, path, filename)
            #print(e)


if __name__ == '__main__':
    pass

