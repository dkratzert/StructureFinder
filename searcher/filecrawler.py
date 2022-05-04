#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <dkratzert@gmx.de> wrote this file. As long as you retain this
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
import zipfile

from searcher import database_handler
from searcher.fileparser import Cif
from searcher.misc import vol_unitcell, get_value
from structurefinder.shelxfile.dsrmath import frac_to_cart
from structurefinder.shelxfile.shelx import ShelXFile

DEBUG = False

excluded_names = ['ROOT',
                  '.OLEX',
                  'olex',
                  'TMP',
                  'TEMP',
                  'Papierkorb',
                  'Recycle.Bin',
                  'dsrsaves',
                  'BrukerShelXlesaves',
                  'shelXlesaves'
                  ]


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
            # print("Error: '{}' in file {}".format(e, self.filepath.encode(encoding='utf-8', errors='ignore')))
            # print(e, self.filepath)  # filepath is not utf-8 save
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
                self.cifpath, self.cifname = os.path.split(name)
                if self.cifname.endswith('.cif'):
                    yield tfile.extractfile(name).read().decode('utf-8', 'ignore').splitlines(keepends=True)
        except Exception as e:
            # print("Error: '{}' in file {}".format(e, self.filepath.encode(encoding='utf-8', errors='ignore')))
            # print(e, self.filepath)  # filepath is not utf-8 save
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


def filewalker_walk(startdir: str, patterns: list):
    """
    walks through the filesystem starting from startdir and searches
    for files with ending endings.

    Since os.walk() uses scandir, it is as fast as pathlib.
    """
    filelist = []
    print('collecting {} files below '.format(', '.join(patterns)) + startdir)
    for root, _, files in os.walk(startdir):
        for filen in files:
            omit = False
            if any(fnmatch.fnmatch(filen, pattern) for pattern in patterns):
                for ex in excluded_names:
                    if re.search(ex, root, re.I):
                        omit = True
                if omit:
                    continue
                fullpath = os.path.abspath(os.path.join(root, filen))
                try:
                    if os.stat(fullpath).st_size == 0:
                        continue
                except Exception:
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


def fill_db_with_cif_data(cif: Cif, filename: str, path: str, structure_id: int,
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
    a = get_value(cif._cell_length_a)
    b = get_value(cif._cell_length_b)
    c = get_value(cif._cell_length_c)
    alpha = get_value(cif._cell_angle_alpha)
    beta = get_value(cif._cell_angle_beta)
    gamma = get_value(cif._cell_angle_gamma)
    volume = get_value(cif._cell_volume)
    if not all((a, b, c, alpha, beta, gamma)):
        return False
    if not volume or volume == "?":
        try:
            volume = str(vol_unitcell(a, b, c, alpha, beta, gamma))
        except ValueError:
            volume = ''
    # Unused value:
    measurement_id = 1
    structures.fill_structures_table(path, filename, structure_id, measurement_id, cif.cif_data['data'])
    structures.fill_cell_table(structure_id, a, b, c, alpha, beta, gamma, volume)
    sum_formula_dict = {}
    for x in cif.atoms:
        #  0     1   2 3 4    5       6
        # [Name type x y z occupancy part]
        try:
            try:
                disord = int(x[6])
            except (KeyError, ValueError, IndexError):
                disord = 0
            try:
                occu = x[5]
            except (KeyError, ValueError, IndexError):
                occu = 1.0
            try:
                atom_type_symbol = x[1]
            except (KeyError, IndexError):
                continue
            elem = atom_type_symbol.capitalize()
            try:
                name = x[0]
            except IndexError:
                continue
            try:
                xc, yc, zc = frac_to_cart([x[2], x[3], x[4]], [a, b, c, alpha, beta, gamma])
                structures.fill_atoms_table(structure_id, name, atom_type_symbol,
                                            x[2], x[3], x[4], occu, disord, round(xc, 5), round(yc, 5), round(zc, 5))
            except ValueError:
                pass
                # print(cif.cif_data['data'], path, filename)
            if elem in sum_formula_dict:
                sum_formula_dict[elem] += occu
            else:
                sum_formula_dict[elem] = occu
        except KeyError as e:
            # print(x, filename, e)
            pass
    cif.cif_data['calculated_formula_sum'] = sum_formula_dict
    structures.fill_residuals_table(structure_id, cif)
    return True


def fill_db_with_res_data(res: ShelXFile, filename: str, path: str, structure_id: int,
                          structures: database_handler.StructureTable, options: dict):
    if not res.cell:
        return False
    if not all([res.cell.a, res.cell.b, res.cell.c, res.cell.al, res.cell.be, res.cell.ga]):
        return False
    if not res.cell.volume:
        return False
    # Unused value:
    measurement_id = 1
    structures.fill_structures_table(path, filename, structure_id, measurement_id, res.titl)
    structures.fill_cell_table(structure_id, res.cell.a, res.cell.b, res.cell.c, res.cell.al,
                               res.cell.be, res.cell.ga, res.cell.volume)
    for at in res.atoms:
        if at.qpeak:
            continue
        if at.element.lower() == 'cnt':  # Do not add Shelxle centroids
            continue
        structures.fill_atoms_table(structure_id,
                                    at.name,
                                    at.element.capitalize(),
                                    at.x,
                                    at.y,
                                    at.z,
                                    at.sof,
                                    at.part.n,
                                    round(at.xc, 5), round(at.yc, 5), round(at.zc, 5))
    cif = Cif(options=options)
    cif.cif_data["_cell_formula_units_Z"] = res.Z
    try:
        cif.cif_data["_space_group_symop_operation_xyz"] = "\n".join([repr(x) for x in res.symmcards])
    except IndexError:
        pass
    try:
        cif.cif_data["calculated_formula_sum"] = res.sum_formula_ex_dict()
    except ZeroDivisionError:
        pass
    try:
        cif.cif_data["_chemical_formula_sum"] = res.sum_formula_exact
    except ZeroDivisionError:
        pass
    cif.cif_data["_diffrn_radiation_wavelength"] = res.wavelen
    if res.R1:
        cif.cif_data["_refine_ls_R_factor_gt"] = res.R1
    if res.wR2:
        cif.cif_data["_refine_ls_wR_factor_ref"] = res.wR2
    if res.parameters:
        cif.cif_data['_refine_ls_number_parameters'] = res.parameters
    if res.data:
        cif.cif_data['_refine_ls_number_reflns'] = res.data
    if res.num_restraints:
        cif.cif_data['_refine_ls_number_restraints'] = res.num_restraints
    if res.temp_in_Kelvin:
        cif.cif_data['_diffrn_ambient_temperature'] = round(res.temp_in_Kelvin, 5)
    if res.dhole:
        cif.cif_data['_refine_diff_density_min'] = res.dhole
    if res.hpeak:
        cif.cif_data['_refine_diff_density_max'] = res.hpeak
    if res.latt:
        cif.cif_data['_space_group_centring_type'] = res.latt.N_str
    if res.space_group:
        cif.cif_data["_space_group_name_H-M_alt"] = res.space_group
    if res.goof:
        cif.cif_data["_refine_ls_goodness_of_fit_ref"] = res.goof
    if res.rgoof:
        cif.cif_data["_refine_ls_restrained_S_all"] = res.rgoof
    try:
        cif.cif_data["_shelx_res_file"] = str(res)
    except IndexError:
        pass
    structures.fill_residuals_table(structure_id, cif)
    return True


if __name__ == '__main__':
    z = MyTarReader('./test-data/106c.tar.bz2')

    for i in z:
        print(i)

    # filewalker_walk('./')
    # z = zipopener('../test-data/Archiv.zip')
    # print(z)

    # fp = create_file_list('../test-data/', 'zip')
    # for i in fp:
    #    print(i)
