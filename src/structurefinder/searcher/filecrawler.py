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
import re
import tarfile
import zipfile
from typing import Generator, Tuple, List, Union

import gemmi

from structurefinder.searcher import database_handler
from structurefinder.searcher.fileparser import CifFile
from structurefinder.searcher.misc import get_value
from structurefinder.shelxfile.shelx import ShelXFile

DEBUG = False

excluded_names = ('ROOT',
                  '.OLEX',
                  'olex',
                  'TMP',
                  'TEMP',
                  'Papierkorb',
                  'Recycle.Bin',
                  'dsrsaves',
                  'BrukerShelXlesaves',
                  'shelXlesaves')


class MyZipBase(object):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.cifname = ''
        self.cifpath = ''
        self.filenames: Union[List, None] = None


class MyZipReader(MyZipBase):
    def __init__(self, filepath):
        """
        extracts .cif files from zip files
        """
        super().__init__(filepath)
        self.zfile = zipfile.ZipFile(self.filepath)
        self.filenames = [x for x in self.zfile.namelist() if x.endswith('.cif')]

    def __len__(self):
        return len(self.filenames)

    def __iter__(self) -> Generator:
        """
        returns an iterator of cif files in the zipfile as list.
        """
        try:
            for name in self.filenames:
                if name.startswith('__'):
                    continue
                if self.zfile.NameToInfo[name].file_size < 150000000:
                    doc = gemmi.cif.Document()
                    doc.source = name
                    doc.parse_string(self.zfile.read(name).decode('ascii', 'ignore'))
                    if doc:
                        yield doc
                    else:
                        continue
        except Exception as e:
            if DEBUG:
                print("Error: '{}' in file {}".format(e, self.filepath.encode(encoding='utf-8', errors='ignore')))
                print(e, self.filepath)  # filepath is not utf-8 save
            yield None


class MyTarReader(MyZipBase):
    def __init__(self, filepath):
        """
        extracts .cif files from tar.gz files
        """
        super().__init__(filepath)
        self.tfile = tarfile.open(self.filepath, mode='r')
        self.filenames = [x for x in self.tfile.getnames() if x.endswith('.cif')]

    def __len__(self):
        return len(self.filenames)

    def __iter__(self) -> Generator:
        """
        returns an iterator of cif files in the zipfile as list.
        """
        try:
            for name in self.filenames:
                doc = gemmi.cif.Document()
                doc.source = name
                doc.parse_string(self.tfile.extractfile(name).read().decode('ascii', 'ignore'))
                if doc:
                    yield doc
                else:
                    continue
        except Exception as e:
            if DEBUG:
                print("Error: '{}' in file {}".format(e, self.filepath.encode(encoding='utf-8', errors='ignore')))
                print(e, self.filepath)  # filepath is not utf-8 save
            yield None


def filewalker_walk(startdir: str, patterns: list, excludes: List[str]) -> Tuple[Tuple[str, str], ...]:
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
                for ex in excludes:
                    if re.search(ex, root, re.I):
                        omit = True
                        break
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
                filelist.append((root, filen))
            else:
                continue
    return tuple(filelist)


def fill_db_with_cif_data(cif: CifFile, filename: str, path: str, structure_id: int,
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
    sum_formula_dict = {}
    measurement_id = 1
    structures.fill_structures_table(path, filename, structure_id, measurement_id, cif.block.name)
    structures.fill_cell_table(structure_id, cif.cell.a, cif.cell.b, cif.cell.c,
                               cif.cell.alpha, cif.cell.beta, cif.cell.gamma, cif.cell.volume)
    try:
        sum_formula_dict = add_atoms(cif, structure_id, structures)
    except AttributeError as e:
        print('Atoms crashed', e, structure_id)
    cif.cif_data['calculated_formula_sum'] = sum_formula_dict
    structures.fill_residuals_table(structure_id, cif)
    structures.fill_authors_table(structure_id, cif)
    return True


def add_atoms(cif, structure_id, structures):
    sum_formula_dict = {}
    for at, orth in zip(cif.atoms, cif.atoms_orth):
        try:
            try:
                part = at.part
                if part in {'.', '', '?'}:
                    part = 0
            except (KeyError, ValueError, IndexError):
                part = 0
            try:
                occu = get_value(at.occ)
                if not occu:
                    occu = 1.0
            except (KeyError, ValueError, IndexError):
                occu = 1.0
            try:
                structures.fill_atoms_table(structure_id, at.label, at.type,
                                            get_value(at.x), get_value(at.y), get_value(at.z),
                                            occu, part,
                                            orth.x, orth.y, orth.z)
            except ValueError:
                pass
                # print(cif.cif_data['data'], structure_id)
            if at.type in sum_formula_dict:
                sum_formula_dict[at.type] += occu
            else:
                sum_formula_dict[at.type] = occu
        except KeyError as e:
            # print(at, structure_id, e)
            pass
    return sum_formula_dict


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
    cif = CifFile(options=options)
    cif.cif_data["_cell_formula_units_Z"] = res.Z
    try:
        symmops = "\n".join([x.to_fractional() for x in res.symmcards])
        # gemmi needs integer ratio instead of float values in symmcards:
        # symmops = "\n".join([x.toShelxl() for x in res.symmcards])
        cif.cif_data["_space_group_symop_operation_xyz"] = symmops
    except Exception:
        try:
            symmops = "\n".join([x.toShelxl() for x in res.symmcards])
            cif.cif_data["_space_group_symop_operation_xyz"] = symmops
        except Exception:
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
    if cif.cif_data["_space_group_symop_operation_xyz"]:
        try:
            symm_ops = cif.cif_data["_space_group_symop_operation_xyz"].splitlines(keepends=False)
            spgr: gemmi.SpaceGroup = gemmi.find_spacegroup_by_ops(gemmi.GroupOps([gemmi.Op(o) for o in symm_ops]))
            if spgr:
                cif.cif_data["_space_group_name_H-M_alt"] = spgr.short_name()
                cif.cif_data['_space_group_IT_number'] = spgr.number
                cif.cif_data["_space_group_centring_type"] = spgr.centring_type()
        except RuntimeError as e:
            # print(e, filename)
            pass
    if res.space_group and not cif.cif_data["_space_group_name_H-M_alt"]:
        cif.cif_data["_space_group_name_H-M_alt"] = res.space_group
        try:
            spgr = gemmi.find_spacegroup_by_name(str(res.space_group).replace(')', '').replace('(', ''))
            if not cif.cif_data['_space_group_IT_number']:
                cif.cif_data['_space_group_IT_number'] = spgr.number
        except AttributeError:
            pass
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
    z = MyTarReader('./tests/test-data/106c.tar.bz2')

    for i in z:
        print(i)

    # filewalker_walk('./')
    # z = zipopener('./tests/test-data/Archiv.zip')
    # print(z)

    # fp = create_file_list('../test-data/', 'zip')
    # for i in fp:
    #    print(i)
