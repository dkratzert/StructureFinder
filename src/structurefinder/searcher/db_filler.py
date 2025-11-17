#!/usr/bin/python3
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


import gemmi
from shelxfile import Shelxfile

from structurefinder.searcher import database_handler
from structurefinder.searcher.crawler import Result
from structurefinder.searcher.cif_file import CifFile
from structurefinder.searcher.misc import get_value

DEBUG = False


def fill_db_with_cif_data(cif: CifFile, filename: str, path: str, structure_id: int,
                          structures: database_handler.StructureTable):
    """
    Fill all info from cif file into the database tables
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
    for at, orth in zip(cif.atoms, cif.atoms_orth, strict=True):
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
        except KeyError:
            # print(at, structure_id, e)
            pass
    return sum_formula_dict


def fill_db_with_res_data(res: Shelxfile, result: Result, structure_id: int, structures: database_handler.StructureTable):
    if not res.cell:
        return False
    if not all([res.cell.a, res.cell.b, res.cell.c, res.cell.alpha, res.cell.beta, res.cell.gamma]):
        return False
    if not res.cell.volume:
        return False
    # Unused value:
    measurement_id = 1
    path = result.file_path if not result.archive_path else result.archive_path
    structures.fill_structures_table(path, result.filename, structure_id, measurement_id, res.titl)
    structures.fill_cell_table(structure_id, res.cell.a, res.cell.b, res.cell.c, res.cell.alpha,
                               res.cell.beta, res.cell.gamma, res.cell.volume)
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
    cif = CifFile()
    cif.cif_data['file_size'] = result.file_size
    cif.cif_data['modification_time'] = result.modification_time
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
        cif.cif_data["calculated_formula_sum"] = res.sum_formula_exact_as_dict()
    except ZeroDivisionError:
        pass
    try:
        cif.cif_data["_chemical_formula_sum"] = res.sum_formula_exact
    except ZeroDivisionError:
        pass
    cif.cif_data["_diffrn_radiation_wavelength"] = res.wavelength
    if res.R1:
        cif.cif_data["_refine_ls_R_factor_gt"] = res.R1
    if res.wr2:
        cif.cif_data["_refine_ls_wR_factor_ref"] = res.wr2
    if res.parameters:
        cif.cif_data['_refine_ls_number_parameters'] = res.parameters
    if res.data:
        cif.cif_data['_refine_ls_number_reflns'] = res.data
    if res.num_restraints:
        cif.cif_data['_refine_ls_number_restraints'] = res.num_restraints
    if res.temp_in_kelvin:
        cif.cif_data['_diffrn_ambient_temperature'] = round(res.temp_in_kelvin, 5)
    if res.deepest_hole:
        cif.cif_data['_refine_diff_density_min'] = res.deepest_hole
    if res.highest_peak:
        cif.cif_data['_refine_diff_density_max'] = res.highest_peak
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
        except RuntimeError:
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
    except Exception:
        pass
    structures.fill_residuals_table(structure_id, cif)
    return True
