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
import fnmatch
import time
import os
import re
import pathlib
import sys
import zipfile

import lattice.lattice
import searcher.atoms
import searcher.database_handler
import searcher.fileparser


excluded_names = ['ROOT', '.OLEX', 'TMP', 'TEMP', 'Papierkorb', 'Recycle.Bin']


def zipopener(file: os.path) -> list:
    """
    Opens a zip file and returns a list of cif files in the zip file.
    """
    names = []
    try:
        if not zipfile.is_zipfile(file):
            return []
        with zipfile.ZipFile(file, 'r') as myzip:
            for f in myzip.filelist:
                if f.filename.endswith('.cif'):
                    if not f.filename.startswith('__') and f.file_size < 150000000:
                        # print(f.filename)  # for testing
                        names.append(f)
    except (zipfile.BadZipFile, zipfile.LargeZipFile):
        return []
    return names


def create_file_list(searchpath='None', ending='cif'):
    """
    walks through the file system and collects cells from res/cif files
    """
    if not os.path.isdir(searchpath):
        print('search path {0} not found! Or no directory!'.format(searchpath))
        sys.exit()
    print('collecting files... (may take some minutes)')
    p = pathlib.Path(searchpath)
    paths = p.rglob("*.{}".format(ending))
    return paths


def filewalker_walk(startdir, add_excludes=''):
    """
    walks through the filesystem starting from startdir and searches
    for files with ending endings.
    """
    filelist = []
    excludes = []
    if add_excludes:
        excludes.extend(add_excludes)
    excludes = excluded_names
    print('collecting files below ' + startdir)
    for root, _, files in os.walk(startdir):
        for filen in files:
            if fnmatch.fnmatch(filen, '*.cif') or fnmatch.fnmatch(filen, '*.zip'):
                fullpath = os.path.join(root, filen)
                #print(fullpath)
                if os.stat(fullpath).st_size == 0:
                    continue
                for ex in excludes:
                    if re.search(ex, fullpath, re.I):
                        continue
                if filen == 'xd_geo.cif':  # Exclude xdgeom cif files
                    continue
                if filen == 'xd_four.cif':  # Exclude xdfourier cif files
                    continue
                filelist.append([root, filen])
            else:
                continue
    return filelist


def put_cifs_in_db(self=None, searchpath='', dbfilename="structuredb.sqlite"):
    """
    Imports cif files from a certain directory
    :return: None
    """
    lastid = 1
    if self:
        # the graphical version:
        import PyQt5.QtWidgets
        self.tmpfile = True
        self.statusBar().showMessage('')
        self.close_db()
        self.start_db()
        fname = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        structures = self.structures
        # This can not work in the gui, because we don't have a database file in every case (tmpfile):
        #db = searcher.database_handler.DatabaseRequest(os.path.join(fname, dbfilename))
    else:
        # the command line version
        fname = searchpath
        db = searcher.database_handler.DatabaseRequest(dbfilename)
        db.initialize_db()
        lastid = db.get_lastrowid()
        if not lastid:
            lastid = 0
        structures = searcher.database_handler.StructureTable(dbfilename)
    if not fname:
        return False
    if self:
        self.ui.cifList_treeWidget.show()
        self.abort_import_button.show()
    # TODO: implement multiple cells in one cif file:
    if lastid <= 1:
        n = 1
    else:
        n = lastid + 1
    min = 0
    prognum = 0
    num = 1
    time1 = time.clock()
    filelist = filewalker_walk(str(fname))
    for filepth, name in filelist:
        cifok = False
        fullpath = os.path.join(filepth, name)
        cif = searcher.fileparser.Cif()
        if prognum == 20:
            prognum = 0
        if self:
            self.progressbar(prognum, min, 20)
        # This is really ugly copy&pase code. TODO: refractor this:
        if name.endswith('.cif'):
            with open(fullpath, mode='r', encoding='ascii', errors="ignore") as f:
                try:
                    cifok = cif.parsefile(f.readlines())
                    if not cifok:
                        continue
                except IndexError:
                    continue
                if cif:
                    tst = fill_db_tables(cif, filename=name, path=filepth, structure_id=n, structures=structures)
                    if not tst:
                        continue
                    if self:
                        self.add_table_row(name, filepth, cif.cif_data['data'], str(n))
                    n += 1
                    num += 1
                    if n % 1000 == 0:
                        print('{} files ...'.format(n))
                        structures.database.commit_db()
                    prognum += 1
        else:  # a zip file:
            try:
                with zipfile.ZipFile(fullpath, 'r') as myzip:
                    for z in zipopener(fullpath):
                        with myzip.open(z.filename, mode='r') as zippedfile:
                            filedata = zippedfile.read().decode('ascii', 'ignore')
                            try:
                                cifok = cif.parsefile(filedata.splitlines())
                                if not cifok:
                                    continue
                            except IndexError:
                                continue
                            if cif:
                                tst = fill_db_tables(cif, filename=z.filename, path=fullpath, structure_id=n, structures=structures)
                                if not tst:
                                    print('#####', fullpath)
                                    continue
                                if self:
                                    self.add_table_row(z.filename, fullpath, cif.cif_data['data'], str(n))
                                n += 1
                                num += 1
                                if n % 1000 == 0:
                                    print('{} files ...'.format(n))
                                    structures.database.commit_db()
                                prognum += 1
            except zipfile.BadZipFile:
                continue
        if self:
            if not self.decide_import:
                # This means, import was aborted.
                self.abort_import_button.hide()
                self.decide_import = True
                break
    if self:
        self.progress.hide()
    structures.populate_fulltext_search_table()
    structures.database.commit_db("Committed")
    time2 = time.clock()
    diff = time2 - time1
    m, s = divmod(diff, 60)
    h, m = divmod(m, 60)
    tmessage = 'Added {} cif files to database in: {:>2d} h, {:>2d} m, {:>3.2f} s'
    if self:
        self.ui.statusbar.showMessage(tmessage.format(num-1, int(h), int(m), s))
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        #self.ui.cifList_treeWidget.resizeColumnToContents(1)
        #self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.abort_import_button.hide()
    else:
        print(tmessage.format(num - 1, int(h), int(m), s))



def fill_db_tables(cif: searcher.fileparser.Cif, filename: str, path: str, structure_id: str,
                   structures: searcher.database_handler.StructureTable):
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
            volume = lattice.lattice.vol_unitcell(a, b, c, alpha, beta, gamma)
            volume = str(volume)
        except ValueError:
            volume = ''
    measurement_id = structures.fill_measuremnts_table(filename, structure_id)
    structures.fill_structures_table(path, filename, structure_id, measurement_id, cif.cif_data['data'])
    structures.fill_cell_table(structure_id, a, b, c, alpha, beta, gamma, volume)
    #pprint(cif._atom)
    for x in cif._atom:
        try:
            try:
                disord = cif._atom[x]['_atom_site_disorder_group']
            except KeyError:
                disord = "0"
            try:
                occu = cif._atom[x]['_atom_site_occupancy'].split('(')[0]
            except KeyError:
                occu = "1"
            try:
                atom_type_symbol = cif._atom[x]['_atom_site_type_symbol']
            except KeyError:
                atom_type_symbol  = searcher.atoms.get_atomlabel(x)
            structures.fill_atoms_table(structure_id, x,
                                         atom_type_symbol,
                                         cif._atom[x]['_atom_site_fract_x'].split('(')[0],
                                         cif._atom[x]['_atom_site_fract_y'].split('(')[0],
                                         cif._atom[x]['_atom_site_fract_z'].split('(')[0],
                                         occu,
                                         disord
                                        )
        except KeyError as e:
            #print(x, filename)
            pass
    structures.fill_residuals_table(structure_id, cif)
    return True


if __name__ == '__main__':
    z = zipopener('../test-data/Archiv.zip')
    print(z)

    #fp = create_file_list('../test-data/', 'zip')
    #for i in fp:
    #    print(i)