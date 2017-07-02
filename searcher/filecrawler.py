#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <daniel.kratzert@uni-freiburg.de> wrote this file. As long as you retain this 
* notice you can do whatever you want with this stuff. If we meet some day, and 
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: Daniel Kratzert
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
    p = Path(searchpath)
    paths = p.rglob("*.cif")
    return paths


def filewalker_walk(startdir, endings, add_excludes=''):
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
        if n % 400 == 0:
            print('{} files ...'.format(n))
            structures.database.commit_db()
    time2 = time.clock()
    diff = time2 - time1
    spinner.stop()
    print('\nAdded {} cif files to database in: {} s'.format(n, round(diff, 2)))
    structures.populate_fulltext_search_table()
    structures.database.commit_db("Committed")


def fill_db_tables(cif, filename, path, structure_id, structures):
    """
    Fill all info from cif file into the database tables
    _atom_site_label
    _atom_site_type_symbol
    _atom_site_fract_x
    _atom_site_fract_y
    _atom_site_fract_z
    _atom_site_U_iso_or_equiv
    _atom_site_adp_type
    _atom_site_occupancy
    _atom_site_site_symmetry_order
    _atom_site_calc_flag
    _atom_site_refinement_flags_posn
    _atom_site_refinement_flags_adp
    _atom_site_refinement_flags_occupancy
    _atom_site_disorder_assembly
    _atom_site_disorder_group
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
    volume = cif._cell_volume
    if not all((a, b, c, alpha, beta, gamma)):
        return False
    measurement_id = structures.fill_measuremnts_table(filename, structure_id)
    structures.fill_structures_table(path, filename, structure_id, measurement_id, cif.cif_data['data'])
    structures.fill_cell_table(structure_id, a, b, c, alpha, beta, gamma, volume)
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
    structures.fill_residuals_table(structure_id, cif)
    return True


if __name__ == '__main__':
    pass

