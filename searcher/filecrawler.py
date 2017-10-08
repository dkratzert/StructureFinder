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
import os
import pathlib
import re
import sys
import tarfile
import time
import zipfile

from searcher import atoms, database_handler, fileparser
from lattice.lattice import vol_unitcell

excluded_names = ['ROOT',
                  '.OLEX',
                  'TMP',
                  'TEMP',
                  'Papierkorb',
                  'Recycle.Bin']


class MyZipBase(object):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.cifname = ''
        self.cifpath = ''


class MyZipReader(MyZipBase):
    def __init__(self, filepath):
        """
        extracts .cif files from zip files
        """
        super().__init__(filepath)

    def __iter__(self) -> list:
        """
        returns an iterator of cif files in the zipfile as list.
        """
        try:
            zfile = zipfile.ZipFile(self.filepath)
            for name in zfile.namelist():
                (self.cifpath, self.cifname) = os.path.split(name)
                if self.cifname.endswith('.cif'):
                    if not self.cifname.startswith('__') and zfile.NameToInfo[name].file_size < 150000000:
                        yield zfile.read(name).decode('utf-8', 'ignore').splitlines(keepends=True)
        except Exception as e:
            #print("Error: '{}' in file {}".format(e, self.filepath.encode(encoding='utf-8', errors='ignore')))
            #print(e, self.filepath)  # filepath is not utf-8 save
            yield []


class MyTarReader(MyZipBase):
    def __init__(self, filepath):
        """
        extracts .cif files from tar.gz files
        """
        super().__init__(filepath)

    def __iter__(self) -> list:
        """
        returns an iterator of cif files in the zipfile as list.
        """
        try:
            tfile = tarfile.open(self.filepath, mode='r')
            for name in tfile.getnames():
                (self.cifpath, self.cifname) = os.path.split(name)
                if self.cifname.endswith('.cif'):
                    yield tfile.extractfile(name).read().decode('utf-8', 'ignore').splitlines(keepends=True)
        except Exception as e:
            #print("Error: '{}' in file {}".format(e, self.filepath.encode(encoding='utf-8', errors='ignore')))
            #print(e, self.filepath)  # filepath is not utf-8 save
            yield []


def create_file_list(searchpath='None', ending='cif'):
    """
    walks through the file system and collects cells from res/cif files.
    Pathlib is nice, but does not allow me to do rglob for more than one file type.
    """
    if not os.path.isdir(searchpath):
        print('search path {0} not found! Or no directory!'.format(searchpath))
        sys.exit()
    print('collecting files... (may take some minutes)')
    p = pathlib.Path(searchpath)
    paths = p.rglob("*.{}".format(ending))
    return paths


def filewalker_walk(startdir):
    """
    walks through the filesystem starting from startdir and searches
    for files with ending endings.

    Since os.walk() uses scandir, it is as fast as pathlib.
    """
    filelist = []
    patterns = ('*.cif', '*.zip', '*.tar.gz', '*.tar.bz2', '*.tgz')
    print('collecting files below ' + startdir)
    for root, _, files in os.walk(startdir):
        for filen in files:
            omit = False
            if any(fnmatch.fnmatch(filen, pattern) for pattern in patterns):
                fullpath = os.path.abspath(os.path.join(root, filen))
                if os.stat(fullpath).st_size == 0:
                    continue
                for ex in excluded_names:
                    if re.search(ex, fullpath, re.I):
                        omit = True
                if omit:
                    continue
                if filen == 'xd_geo.cif':  # Exclude xdgeom cif files
                    continue
                if filen == 'xd_four.cif':  # Exclude xdfourier cif files
                    continue
                # This is much faster than yield():
                filelist.append([root, filen])
            else:
                continue
    return filelist


def put_cifs_in_db(self=None, searchpath: str = './', excludes: list = None, lastid: int = 1, structures=None) -> int:
    """
    Imports cif files from a certain directory
    """
    if excludes:
        excluded_names.extend(excludes)
    if not searchpath:
        return 0
    if self:
        structures = self.structures
    if lastid <= 1:
        n = 1
    else:
        n = lastid
    prognum = 0
    num = 1
    zipcifs = 0
    time1 = time.clock()
    filelist = filewalker_walk(str(searchpath))
    options = {}
    for filepth, name in filelist:
        fullpath = os.path.join(filepth, name)
        options['modification_time'] = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(fullpath)))
        options['file_size'] = int(os.stat(str(fullpath)).st_size)
        cif = fileparser.Cif(options=options)
        if self:
            if prognum == 20:
                prognum = 0
            self.progressbar(prognum, 0, 20)
        # This is really ugly copy&pase code. TODO: refractor this:
        if name.endswith('.cif'):
            with open(fullpath, mode='r', encoding='ascii', errors="ignore") as f:
                try:
                    cifok = cif.parsefile(f.readlines())
                    if not cifok:
                        continue
                except IndexError:
                    continue
                if cif:  # means cif object has data inside (cif could be parsed)
                    tst = fill_db_tables(cif, filename=name, path=filepth, structure_id=n,
                                         structures=structures)
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
            if fullpath.endswith('.zip'):
                z = MyZipReader(fullpath)
            else:
                z = MyTarReader(fullpath)
            for zippedfile in z:              # the list of cif files in the zip file
                omit = False
                for ex in excluded_names:          # remove excludes
                    if re.search(ex, z.cifpath, re.I):
                        omit = True
                if omit:
                    continue
                try:
                    cifok = cif.parsefile(zippedfile)
                    if not cifok:
                        continue
                except IndexError:
                    continue
                if cif:
                    tst = fill_db_tables(cif, filename=z.cifname, path=fullpath,
                                         structure_id=str(n), structures=structures)
                    zipcifs += 1
                    if not tst:
                        continue
                    if self:
                        self.add_table_row(name=z.cifname, path=fullpath,
                                           data=cif.cif_data['data'], structure_id=str(n))
                    n += 1
                    num += 1
                    if n % 1000 == 0:
                        print('{} files ...'.format(n))
                        structures.database.commit_db()
                    prognum += 1
        if self:
            if not self.decide_import:
                # This means, import was aborted.
                self.abort_import_button.hide()
                self.decide_import = True
                break
    structures.database.commit_db()
    time2 = time.clock()
    diff = time2 - time1
    m, s = divmod(diff, 60)
    h, m = divmod(m, 60)
    tmessage = 'Added {0} cif files ({4} in compressed files) to database in: {1:>2d} h, {2:>2d} m, {3:>3.2f} s'
    print(tmessage.format(num - 1, int(h), int(m), s, zipcifs))
    if self:
        self.ui.statusbar.showMessage(tmessage.format(num - 1, int(h), int(m), s, zipcifs))
    return n-1


def fill_db_tables(cif: fileparser.Cif, filename: str, path: str, structure_id: str,
                   structures: database_handler.StructureTable):
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
            volume = str(vol_unitcell(a, b, c, alpha, beta, gamma))
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
                atom_type_symbol  = atoms.get_atomlabel(x)
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
    z = MyTarReader('./test-data/106c.tar.bz2')

    for i in z:
        print(i)

    #filewalker_walk('./')
    #z = zipopener('../test-data/Archiv.zip')
    #print(z)

    #fp = create_file_list('../test-data/', 'zip')
    #for i in fp:
    #    print(i)