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
import time
import re
import fnmatch as fn
import sys
from pathlib import Path
from pprint import pprint

from lattice import lattice
from searcher.database_handler import StructureTable, DatabaseRequest
from searcher.fileparser import Cif


excluded_names = (
        {'ROOT', '.OLEX', 'TMP', 'TEMP', 'akfischer', 'Papierkorb', 'Recycle.Bin'}
    )


def create_file_list(searchpath='None', ending='cif'):
    """
    walks through the file system and collects cells from res/cif files
    into a database
    """
    if not os.path.isdir(searchpath):
        print('search path {0} not found! Or no directory!'.format(searchpath))
        sys.exit()
    print('collecting files... (may take some minutes)')
    p = Path(searchpath)
    paths = p.rglob("*.{}".format(ending))
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
    """
    Command line version of file crawler.
    """
    dbfilename = "structuredb.sqlite"
    try:
        os.remove(dbfilename)
    except:
        pass
    db = DatabaseRequest(dbfilename)
    db.initialize_db()
    structures = StructureTable(dbfilename)
    n = 1
    time1 = time.clock()
    cif = Cif()
    for filepth in create_file_list(str(searchpath), ending='cif'):
        if not filepth.is_file():
            continue
        path = str(filepth.parents[0])
        match = False
        if filepth.name == 'xd_geo.cif':
            continue
        for ex in excluded_names:
            if re.search(ex, path, re.I):
                match = True
        if match:
            continue
        try:
            cifok = cif.parsefile(filepth)
        except IndexError:
            continue
        if not cifok:
            continue
        if cif and filepth.name and path:
            tst = fill_db_tables(cif, filepth.name, path, n, structures)
            if not tst:
                continue
            n += 1
        if n % 1000 == 0:
            print('{} files ...'.format(n))
            structures.database.commit_db()
    time2 = time.clock()
    diff = time2 - time1
    m, s = divmod(diff, 60)
    h, m = divmod(m, 60)
    structures.populate_fulltext_search_table()
    structures.database.commit_db("Committed")
    print('\nAdded {} cif files to database in: {:>2} h, {:>2} m, {:>3.2f} s'.format(n-1, h, m, s))


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
    if not volume or volume == "?":
        try:
            if isinstance(a, str):
                a = float(a.split('(')[0])
            if isinstance(b, str):
                b = float(b.split('(')[0])
            if isinstance(c, str):
                c = float(c.split('(')[0])
            if isinstance(alpha, str):
                alpha = float(alpha.split('(')[0])
            if isinstance(beta, str):
                beta = float(beta.split('(')[0])
            if isinstance(gamma, str):
                gamma = float(gamma.split('(')[0])
            volume = lattice.vol_unitcell(a, b, c, alpha, beta, gamma)
            volume = str(volume)
        except ValueError:
            volume = ''
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
                                         cif._atom[x]['_atom_site_fract_z'].split('(')[0],
                                         cif._atom[x]['_atom_site_occupancy'].split('(')[0],
                                         cif._atom[x]['_atom_site_disorder_group']
                                        )
        except KeyError as e:
            pass
    structures.fill_residuals_table(structure_id, cif)
    return True


if __name__ == '__main__':
    pass

