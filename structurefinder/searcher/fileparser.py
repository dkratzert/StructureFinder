# -*- coding: utf-8 -*-
"""
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <dkratzert@gmx.de> wrote this file. As long as you retain this
* notice you can do whatever you want with this stuff. If we meet some day, and
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: daniel
"""
from collections import namedtuple
from typing import List, Dict, Union, Any

import gemmi.cif
from gemmi import cif

from structurefinder.searcher.misc import get_error_from_value
from structurefinder.shelxfile.elements import sorted_atoms

DEBUG = False


class CifFile(object):

    def __init__(self, options=None):
        """
        A cif file parsing object optimized for speed and simplicity.
        It can not handle multi cif files.
        """
        self.doc: Union[None, gemmi.cif.Document] = None
        self.block: Union[None, gemmi.cif.Block] = None
        self.cell: Union[None, gemmi.UnitCell] = None
        if options is None:
            options = {'modification_time': "", 'file_size': ""}
        # This is a set of keys that are already there:
        self.cif_data: Dict[str, Union[str, Any]] = {
            "data"                                : '',
            "_cell_formula_units_Z"               : '',
            "_space_group_name_H-M_alt"           : '',
            "_space_group_name_Hall"              : '',
            "_space_group_centring_type"          : '',
            "_space_group_IT_number"              : '',
            "_space_group_crystal_system"         : '',
            "_space_group_symop_operation_xyz"    : '',
            "_audit_creation_method"              : '',
            "_chemical_formula_sum"               : '',
            "_chemical_formula_weight"            : '',
            "_exptl_crystal_description"          : '',
            "_exptl_crystal_colour"               : '',
            "_exptl_crystal_size_max"             : '',
            "_exptl_crystal_size_mid"             : '',
            "_exptl_crystal_size_min"             : '',
            "_exptl_absorpt_coefficient_mu"       : '',
            "_exptl_absorpt_correction_type"      : '',
            "_exptl_special_details"              : '',
            "_diffrn_ambient_temperature"         : '',
            "_diffrn_radiation_wavelength"        : '',
            "_diffrn_radiation_type"              : '',
            "_diffrn_source"                      : '',
            "_diffrn_measurement_device_type"     : '',
            "_diffrn_reflns_number"               : '',
            "_diffrn_reflns_av_R_equivalents"     : '',
            "_diffrn_reflns_av_unetI/netI"        : '',
            "_diffrn_reflns_theta_min"            : '',
            "_diffrn_reflns_theta_max"            : '',
            "_diffrn_reflns_theta_full"           : '',
            "_diffrn_measured_fraction_theta_max" : '',
            "_diffrn_measured_fraction_theta_full": '',
            "_reflns_number_total"                : '',
            "_reflns_number_gt"                   : '',
            "_reflns_threshold_expression"        : '',
            "_reflns_Friedel_coverage"            : '',
            "_computing_structure_solution"       : '',
            "_computing_structure_refinement"     : '',
            "_refine_special_details"             : '',
            "_refine_ls_abs_structure_Flack"      : '',
            "_refine_ls_structure_factor_coef"    : '',
            "'_refine_ls_hydrogen_treatment'"     : '',
            "_refine_ls_weighting_details"        : '',
            "_refine_ls_number_reflns"            : '',
            "_refine_ls_number_parameters"        : '',
            "_refine_ls_number_restraints"        : '',
            "_refine_ls_R_factor_all"             : '',
            "_refine_ls_R_factor_gt"              : '',
            "_refine_ls_wR_factor_ref"            : '',
            "_refine_ls_wR_factor_gt"             : '',
            "_refine_ls_goodness_of_fit_ref"      : '',
            "_refine_ls_restrained_S_all"         : '',
            "_refine_ls_shift/su_max"             : '',
            "_refine_ls_shift/su_mean"            : '',
            "_refine_diff_density_max"            : '',
            "_refine_diff_density_min"            : '',
            "_diffrn_reflns_av_unetI_netI"        : '',
            "_database_code_depnum_ccdc_archive"  : '',
            "_shelx_res_file"                     : '',
            "_audit_author_name"                  : '',
            "_audit_contact_author_name"          : '',
            "_citation_author_name"               : '',
            "_citation_editor_name"               : '',
            "_publ_contact_author_name"           : '',
            "_publ_contact_author"                : '',
            "_publ_author_name"                   : '',
            "modification_time"                   : options['modification_time'],
            "file_size"                           : options['file_size']
        }

    def parsefile(self, doc: cif.Document) -> bool:
        """
        This method parses the cif file. Currently, only single items and atoms are supported.
        :param txt: cif file as list without line endings
        :return: cif file content
        :rtype: dict
        """
        self.doc: gemmi.cif.Document = doc
        if self.doc.find_block('global'):
            self.block = self.doc.find_block('global')
            # get data from global
            self.block = self.doc.find_block(str(self.doc[1]))
        else:
            try:
                self.block = self.doc[0]
            except IndexError as e:
                print(e)
                return False
        if not self.block:
            print('No block found!')
            return False
        # self.cif_data['_space_group_symop_operation_xyz'] = '\n'.join(self.symm)
        # self.cif_data['file_length_lines']: int = num + 1
        self.cell = self._cell
        if not self.cell:
            print('No cell in cif!')
            return False
        # TODO: implement detection of self.cif_data["_space_group_centring_type"] by symmcards.
        self.fill_data_dict()
        self.handle_deprecates()
        return True

    def fill_data_dict(self):
        self.cif_data['_cell_formula_units_Z'] = self['_cell_formula_units_Z']
        self.cif_data['_space_group_name_H-M_alt'] = self.as_string('_space_group_name_H-M_alt')
        self.cif_data['_space_group_name_Hall'] = self.as_string('_space_group_name_Hall')
        self.cif_data['_space_group_centring_type'] = self.as_string('_space_group_centring_type')
        self.cif_data['_space_group_IT_number'] = self.as_int('_space_group_IT_number')
        self.cif_data['_space_group_crystal_system'] = self.as_string('_space_group_crystal_system')
        self.cif_data['_space_group_symop_operation_xyz'] = '\n'.join(self.symm)
        self.cif_data['_audit_creation_method'] = self.as_string('_audit_creation_method')
        self.cif_data['_chemical_formula_sum'] = self.as_string('_chemical_formula_sum')
        self.cif_data['_chemical_formula_weight'] = self.as_number('_chemical_formula_weight')
        self.cif_data['_exptl_crystal_description'] = self.as_string('_exptl_crystal_description')
        self.cif_data['_exptl_crystal_colour'] = self.as_string('_exptl_crystal_colour')
        self.cif_data['_exptl_crystal_size_max'] = self.as_string('_exptl_crystal_size_max')
        self.cif_data['_exptl_crystal_size_mid'] = self.as_string('_exptl_crystal_size_mid')
        self.cif_data['_exptl_crystal_size_min'] = self.as_string('_exptl_crystal_size_min')
        self.cif_data['_exptl_absorpt_coefficient_mu'] = self.as_number('_exptl_absorpt_coefficient_mu')
        self.cif_data['_exptl_absorpt_correction_type'] = self.as_string('_exptl_absorpt_correction_type')
        self.cif_data['_exptl_special_details'] = self.as_string('_exptl_special_details')
        self.cif_data['_diffrn_ambient_temperature'] = self.as_number('_diffrn_ambient_temperature')
        self.cif_data['_diffrn_radiation_wavelength'] = self.as_number('_diffrn_radiation_wavelength')
        self.cif_data['_diffrn_radiation_type'] = self.as_string('_diffrn_radiation_type')
        self.cif_data['_diffrn_source'] = self.as_string('_diffrn_source')
        self.cif_data['_diffrn_measurement_device_type'] = self.as_string('_diffrn_measurement_device_type')
        self.cif_data['_diffrn_reflns_number'] = self.as_int('_diffrn_reflns_number')
        self.cif_data['_diffrn_reflns_av_R_equivalents'] = self.as_number('_diffrn_reflns_av_R_equivalents')
        self.cif_data['_diffrn_reflns_av_unetI/netI'] = self.as_number('_diffrn_reflns_av_unetI/netI')
        self.cif_data['_diffrn_reflns_theta_min'] = self.as_number('_diffrn_reflns_theta_min')
        self.cif_data['_diffrn_reflns_theta_max'] = self.as_number('_diffrn_reflns_theta_max')
        self.cif_data['_diffrn_reflns_theta_full'] = self.as_number('_diffrn_reflns_theta_full')
        self.cif_data['_diffrn_measured_fraction_theta_max'] = self.as_number('_diffrn_measured_fraction_theta_max')
        self.cif_data['_diffrn_measured_fraction_theta_full'] = self.as_number('_diffrn_measured_fraction_theta_full')
        self.cif_data['_reflns_number_total'] = self.as_int('_reflns_number_total')
        self.cif_data['_reflns_number_gt'] = self.as_int('_reflns_number_gt')
        self.cif_data['_reflns_threshold_expression'] = self.as_string('_reflns_threshold_expression')
        self.cif_data['_reflns_Friedel_coverage'] = self.as_number('_reflns_Friedel_coverage')
        self.cif_data['_computing_structure_solution'] = self.as_string('_computing_structure_solution')
        self.cif_data['_computing_structure_refinement'] = self.as_string('_computing_structure_refinement')
        self.cif_data['_refine_special_details'] = self.as_string('_refine_special_details')
        self.cif_data['_refine_ls_abs_structure_Flack'] = self.as_number('_refine_ls_abs_structure_Flack')
        self.cif_data['_refine_ls_structure_factor_coef'] = self.as_string('_refine_ls_structure_factor_coef')
        self.cif_data['_refine_ls_hydrogen_treatment'] = self.as_string('_refine_ls_hydrogen_treatment')
        self.cif_data['_refine_ls_weighting_details'] = self.as_string('_refine_ls_weighting_details')
        self.cif_data['_refine_ls_number_reflns'] = self.as_int('_refine_ls_number_reflns')
        self.cif_data['_refine_ls_number_parameters'] = self.as_int('_refine_ls_number_parameters')
        self.cif_data['_refine_ls_number_restraints'] = self.as_int('_refine_ls_number_restraints')
        self.cif_data['_refine_ls_R_factor_all'] = self.as_number('_refine_ls_R_factor_all')
        self.cif_data['_refine_ls_R_factor_gt'] = self.as_number('_refine_ls_R_factor_gt')
        self.cif_data['_refine_ls_wR_factor_ref'] = self.as_number('_refine_ls_wR_factor_ref')
        self.cif_data['_refine_ls_wR_factor_gt'] = self.as_number('_refine_ls_wR_factor_gt')
        self.cif_data['_refine_ls_goodness_of_fit_ref'] = self.as_number('_refine_ls_goodness_of_fit_ref')
        self.cif_data['_refine_ls_restrained_S_all'] = self.as_number('_refine_ls_restrained_S_all')
        self.cif_data['_refine_ls_shift/su_max'] = self.as_number('_refine_ls_shift/su_max')
        self.cif_data['_refine_ls_shift/su_mean'] = self.as_number('_refine_ls_shift/su_mean')
        self.cif_data['_refine_diff_density_max'] = self.as_number('_refine_diff_density_max')
        self.cif_data['_refine_diff_density_min'] = self.as_number('_refine_diff_density_min')
        self.cif_data['_diffrn_reflns_av_unetI_netI'] = self.as_number('_diffrn_reflns_av_unetI_netI')
        self.cif_data['_database_code_depnum_ccdc_archive'] = self.as_string('_database_code_depnum_ccdc_archive')
        self.cif_data['_shelx_res_file'] = self.as_string('_shelx_res_file')
        self.cif_data['_audit_author_name'] = self.as_string('_audit_author_name')
        self.cif_data['_audit_contact_author_name'] = self.as_string('_audit_contact_author_name')
        self.cif_data['_citation_author_name'] = self.as_string('_citation_author_name')
        self.cif_data['_citation_editor_name'] = self.as_string('_citation_editor_name')
        self.cif_data['_publ_contact_author_name'] = self.as_string('_publ_contact_author_name')
        self.cif_data['_publ_contact_author'] = self.as_string('_publ_contact_author')
        self.cif_data['_publ_author_name'] = self.as_string('_publ_author_name')

    def as_string(self, cif_key: str) -> str:
        return cif.as_string(self[cif_key]) if self[cif_key] else ''

    def as_int(self, cif_key: str) -> Union[int, None]:
        if self[cif_key]:
            try:
                return cif.as_int(self[cif_key])
            except ValueError as e:
                if DEBUG:
                    print(e, self[cif_key])
                    raise
                return None
        else:
            return None

    def as_number(self, cif_key: str) -> Union[float, None]:
        return cif.as_number(self[cif_key]) if self[cif_key] else ''

    def handle_deprecates(self):
        """
        Makes the old and new cif values equal.
        """
        if self["_symmetry_space_group_name_H-M"]:
            self.cif_data["_space_group_name_H-M_alt"] = self.as_string("_symmetry_space_group_name_H-M")
        if self["_diffrn_measurement_device"]:
            self.cif_data["_diffrn_measurement_device_type"] = self.as_string("_diffrn_measurement_device")
        if self["_refine_ls_shift/esd_max"]:
            self.cif_data["_refine_ls_shift/su_max"] = self.as_number("_refine_ls_shift/esd_max")
        if self['_symmetry_space_group_name_Hall']:
            self.cif_data['_space_group_name_Hall'] = self.as_string('_symmetry_space_group_name_Hall')
        if self['_symmetry_Int_Tables_number']:
            self.cif_data['_space_group_IT_number'] = self.as_int('_symmetry_Int_Tables_number')
        if self['_diffrn_reflns_av_sigmaI/netI']:
            self.cif_data['_diffrn_reflns_av_unetI/netI'] = self.as_number('_diffrn_reflns_av_sigmaI/netI')
        if self["_space_group_name_H-M_alt"] and not self['_space_group_centring_type']:
            try:
                self.cif_data["_space_group_centring_type"] = self.as_string("_space_group_name_H-M_alt").split()[0][0]
            except IndexError:
                pass
        elif self['_space_group_name_Hall'] and not self['_space_group_centring_type']:
            try:
                self.cif_data["_space_group_centring_type"] = \
                self.as_string('_space_group_name_Hall').split()[0].lstrip('-')[0]
            except IndexError:
                pass
        if self['_symmetry_cell_setting']:
            self.cif_data['_space_group_crystal_system'] = self.as_string('_symmetry_cell_setting')

    def __getitem__(self, item) -> str:
        """
        Returns an attribute of the cif data dictionary.
        """
        try:
            return self.block.find_value(item)
        except (KeyError):
            return ''

    @property
    def _cell(self) -> gemmi.UnitCell:
        """
        [12.092, 28.5736, 15.4221, 90.0, 107.365, 90.0]

        _cell_angle_alpha                90.0
        _cell_angle_beta                 107.365(1)
        _cell_angle_gamma                90.00
        _cell_formula_units_Z            4
        _cell_length_a                   12.0920(1)
        _cell_length_b                   28.5736(3)
        _cell_length_c                   15.4221(2)
        """
        a = self['_cell_length_a']
        b = self['_cell_length_b']
        c = self['_cell_length_c']
        alpha = self['_cell_angle_alpha']
        beta = self['_cell_angle_beta']
        gamma = self['_cell_angle_gamma']
        if not all((a, b, c, alpha, beta, gamma)):
            return gemmi.UnitCell()
        return gemmi.UnitCell(cif.as_number(a), cif.as_number(b), cif.as_number(c),
                              cif.as_number(alpha), cif.as_number(beta), cif.as_number(gamma))

    @property
    def volume(self) -> float:
        return self.cell.volume

    @property
    def volume_error_tuple(self):
        return get_error_from_value(self['_cell_volume'])

    @property
    def cell_errors(self):
        a = self['_cell_length_a']
        b = self['_cell_length_b']
        c = self['_cell_length_c']
        alpha = self['_cell_angle_alpha']
        beta = self['_cell_angle_beta']
        gamma = self['_cell_angle_gamma']
        if not all((a, b, c, alpha, beta, gamma)):
            return []
        a = get_error_from_value(a)[1]
        b = get_error_from_value(b)[1]
        c = get_error_from_value(c)[1]
        alpha = get_error_from_value(alpha)[1]
        beta = get_error_from_value(beta)[1]
        gamma = get_error_from_value(gamma)[1]
        return [a, b, c, alpha, beta, gamma]

    def loop_items(self, item: str) -> List[str]:
        return self.block.find_values(item)

    @property
    def atoms(self):
        """
        Atoms from the CIF where values are returned as string like in the CIF with esds.
        """
        labels = self.block.find_loop('_atom_site_label')
        types = self.block.find_loop('_atom_site_type_symbol')
        x = self.block.find_loop('_atom_site_fract_x')
        y = self.block.find_loop('_atom_site_fract_y')
        z = self.block.find_loop('_atom_site_fract_z')
        part = self.block.find_loop('_atom_site_disorder_group')
        occ = self.block.find_loop('_atom_site_occupancy')
        u_eq = self.block.find_loop('_atom_site_U_iso_or_equiv')
        atom = namedtuple('Atom', ('label', 'type', 'x', 'y', 'z', 'part', 'occ', 'u_eq'))
        for label, type, x, y, z, part, occ, u_eq in zip(labels, types, x, y, z,
                                                         part if part else ('0',) * len(labels),
                                                         occ if occ else ('1.000000',) * len(labels),
                                                         u_eq):
            #         0    1   2  3  4   5   6     7
            # yield label, type, x, y, z, part, occ, ueq
            yield atom(label=label, type=type, x=x, y=y, z=z, part=part, occ=occ, u_eq=u_eq)

    @property
    def atoms_orth(self):
        atom = namedtuple('Atom', ('label', 'type', 'x', 'y', 'z', 'part', 'occ', 'u_eq'))
        # try:
        #    cell = self.cell
        # except AttributeError:
        #    yield atom(label='', type='', x=0.0, y=0.0, z=0.0, part=0.0, occ=0.0, u_eq=0.0)
        for at in self.atoms:
            x, y, z = self.cell.orthogonalize(
                gemmi.Fractional(cif.as_number(at.x), cif.as_number(at.y), cif.as_number(at.z)))
            yield atom(label=at.label, type=at.type, x=x, y=y, z=z,
                       part=at.part, occ=at.occ, u_eq=at.u_eq)

    @staticmethod
    def _atom_from_symbol(type_symbol: str) -> str:
        """
        Tries to get an element name from a string like Na1+
        :param type_symbol: a string starting with an element name.
        :return: a real element name
        """
        if type_symbol not in sorted_atoms:
            for n in [2, 1]:
                if type_symbol[:n] in sorted_atoms:
                    type_symbol = type_symbol[:n]
                    break
        return type_symbol

    @property
    def symm(self) -> List[str]:
        """
        Yields symmetry operations.
        ['x, y, z', '-x+1/2, y+1/2, -z+1/2', '-x, -y, -z', 'x-1/2, -y-1/2, z-1/2']
        """
        symm1 = self.block.find_values('_space_group_symop_operation_xyz')
        symm2 = self.block.find_values('_symmetry_equiv_pos_as_xyz')
        return [cif.as_string(x) for x in symm1] if symm1 else [cif.as_string(x) for x in symm2]


if __name__ == '__main__':
    c = CifFile()
    c.parsefile(r'./tests/test-data/COD/4060314.cif')
    print(list(c.symm))

    # c = CifFile()
    # cifok = c.parsefile(r'/Users/daniel/Downloads/j9uwm9c3tmp.cif')
    # pprint(cif.cif_data)
    # pprint(cif._space_group_centring_type)
    # sys.exit()
    # TODO: "_space_group_symop_operation_xyz" or '_symmetry_equiv_pos_as_xyz':
    # print(len(list([x for x in c.atoms])))
    #    pass
    #    print(x)
    # print(cifok)
    # import doctest

    # failed, attempted = doctest.testmod()  # verbose=True)
    # if failed == 0:
    #    print('passed all {} tests!'.format(attempted))
