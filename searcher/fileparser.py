# -*- coding: utf-8 -*-
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
from pathlib import Path
from pprint import pprint
from typing import List, Dict, Union, Any

from searcher.atoms import sorted_atoms


class Cif(object):
    def __init__(self, options=None):
        """
        A cif file parsing object optimized for speed and simplicity.
        It can not handle multi cif files.
        """
        if options is None:
            options = {'modification_time': "", 'file_size': ""}
        # This is a set of keys that are already there:
        self.cif_data: Dict[str, Union[str, Any]] = {
            "data"                                : '',
            "_audit_contact_author_name"          : '',
            "_cell_length_a"                      : '',
            '_cell_length_b'                      : '',
            '_cell_length_c'                      : '',
            '_cell_angle_alpha'                   : '',
            '_cell_angle_beta'                    : '',
            '_cell_angle_gamma'                   : '',
            "_cell_volume"                        : '',
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
            "modification_time"                   : options['modification_time'],
            "file_size"                           : options['file_size']
        }

    def parsefile(self, txt: list) -> bool:
        """
        This method parses the cif file. Currently, only single items and atoms are supported.
        :param txt: cif file as list without line endings
        :return: cif file content
        :rtype: dict
        >>> cif = Cif()
        >>> ok = cif.parsefile(Cif.readfile(r'./test-data/COD/4060314.cif'))
        >>> cif.loops[0]
        {'_publ_author_name': 'Eva Hevia'}
        """
        data: bool = False
        loop: bool = False
        hkl: bool = False
        loophead_list: list = []
        save_frame: bool = False
        loops: List[Dict[str, str]] = []
        loopkey: str = ''
        loop_body: bool = False
        num: int = 0
        semi_colon_text_field: str = ''
        semi_colon_text_list: List[str] = []
        cont: bool = False  # continue to next line if True
        textlen: int = len(txt)
        for num, line in enumerate(txt):
            line: str = line.rstrip('\r\n ')
            if not line:
                loop = False
                loophead_list.clear()
                loopkey = ''
                loop_body = False
                continue
            if line[0] == "_" and loop_body:
                loop = False
                loop_body = False
                loophead_list.clear()
                loopkey = ''
            if loop:
                line = line.lstrip()
                # leave out comments:
                if line[0] == '#':
                    continue
                if line != "loop_" and not loop_body:
                    loopkey = line
                if line[:5] == "loop_":
                    loop = True
                    loop_body = False
                    loophead_list.clear()
                    loopkey = ''
                    continue
                if line[0] != "_":
                    loop_body = True
                # Loop header started, collecting keywords from head:
                if line[0] == "_" and loopkey and not loop_body:
                    loophead_list.append(line)
                    continue
                # We are in a loop and the header ended, so we collect data:
                # A loopitem is a dictionary holding the loop header items as keys and the
                # listed values in the loop body as values:
                if loop_body and loopkey:
                    loopitem = {}  # a line from the loop body, e.g. an atom
                    loop_data_line = self.delimit_line(line)
                    if cont:  # a continuation line
                        cont = False
                        continue
                    # unwrap loop data:
                    if len(loop_data_line) != len(loophead_list):
                        if textlen - 1 > num:
                            loop_data_line.extend(self.delimit_line(txt[num + 1].strip("\r\n ")))
                            # Last check for a not delimited loop body line. At least the parser doesn't
                            # think its a continuation line.
                            if not txt[num + 1].startswith('_'):
                                cont = True
                        continue
                    # add loop item data to the list:
                    for n, item in enumerate(loop_data_line):
                        loopitem[loophead_list[n]] = item
                    if cont:
                        continue
                    loops.append(loopitem)
                continue
            # Find the loop positions:
            if line[:5] == "loop_":
                loop = True
                continue
            # Collect all data items outside loops:
            if line.startswith('_') and not loop:
                lsplit = line.split()
                # add regular cif items:
                if len(lsplit) > 1:
                    self.cif_data[lsplit[0]] = " ".join(self.delimit_line(" ".join(lsplit[1:])))
                    continue
                # add one-liners that are just in the next line:
                if len(lsplit) == 1 and txt[num + 1]:
                    if txt[num + 1][0] != ';' and txt[num + 1][0] != "_":
                        self.cif_data[lsplit[0]] = " ".join(self.delimit_line(txt[num + 1]))
                        continue
            if line.startswith("_shelx_hkl_file") or line.startswith("_refln_"):
                hkl = True
                continue
            # Leave out hkl frames:
            if hkl:
                # break
                continue  # use continue if data should be parsed behind hkl
            if line.lstrip()[0] == ";" and hkl:
                hkl = False
                continue
            if semi_colon_text_field:
                if not line.lstrip().startswith(";"):
                    semi_colon_text_list.append(line)
                    continue  # otherwise, the next line would end the text field
                if line.startswith(";") or line.startswith('_') or line.startswith('loop_'):
                    if not semi_colon_text_list:
                        continue
                    self.cif_data[semi_colon_text_field] = "{}".format(os.linesep).join(semi_colon_text_list)
                    semi_colon_text_list.clear()
                    semi_colon_text_field = ''
                    continue
            if (textlen - 1 > num) and txt[num + 1][0] == ";":
                # if line.startswith("_shelx_res_file"):
                #    break
                # continue  # use continue if data is behind res file
                semi_colon_text_field = line
                continue
            # First find the start of the cif (the data tag)
            if line[:5] == 'data_':
                if line == "data_global":
                    continue
                if not data:
                    name = '_'.join(line.split('_')[1:])
                    self.cif_data['data'] = name
                    data = True
                    continue
                else:  # break in occurence of a second data_
                    break
            # Leave out save_ frames:
            if save_frame:
                continue
            if line[:5] == "save_":
                save_frame = True
                continue
            elif line[:5] == "save_" and save_frame:
                save_frame = False
        self.cif_data['_loop']: List[Dict[str, str]] = loops
        self.cif_data['_space_group_symop_operation_xyz'] = '\n'.join(self.symm)
        self.cif_data['file_length_lines']: int = num + 1
        # TODO: implement detection of self.cif_data["_space_group_centring_type"] by symmcards.
        if not data:
            return False
        # if not atoms:
        #    self.cif_data.clear()
        #    return False
        else:
            self.handle_deprecates()
            return True

    def handle_deprecates(self):
        """
        Makes the old and new cif values equal.
        """
        if "_symmetry_space_group_name_H-M" in self.cif_data:
            self.cif_data["_space_group_name_H-M_alt"] = self.cif_data["_symmetry_space_group_name_H-M"]
        if "_diffrn_measurement_device" in self.cif_data:
            self.cif_data["_diffrn_measurement_device_type"] = self.cif_data["_diffrn_measurement_device"]
        if "_refine_ls_shift/esd_max" in self.cif_data:
            self.cif_data["_refine_ls_shift/su_max"] = self.cif_data["_refine_ls_shift/esd_max"]
        if "_diffrn_measurement_device" in self.cif_data:
            self.cif_data["_diffrn_measurement_device_type"] = self.cif_data["_diffrn_measurement_device"]
        if '_symmetry_space_group_name_Hall' in self.cif_data:
            self.cif_data['_space_group_name_Hall'] = self.cif_data['_symmetry_space_group_name_Hall']
        if '_symmetry_Int_Tables_number' in self.cif_data:
            self.cif_data['_space_group_IT_number'] = self.cif_data['_symmetry_Int_Tables_number']
        if '_diffrn_reflns_av_sigmaI/netI' in self.cif_data:
            self.cif_data['_diffrn_reflns_av_unetI/netI'] = self.cif_data['_diffrn_reflns_av_sigmaI/netI']
        if self.cif_data["_space_group_name_H-M_alt"] and not self._space_group_centring_type:
            try:
                self.cif_data["_space_group_centring_type"] = self.cif_data["_space_group_name_H-M_alt"].split()[0][0]
            except IndexError:
                pass
        elif self._space_group_name_Hall and not self._space_group_centring_type:
            try:
                self.cif_data["_space_group_centring_type"] = self._space_group_name_Hall.split()[0].lstrip('-')[0]
            except IndexError:
                pass
        if self._symmetry_cell_setting:
            self.cif_data['_space_group_crystal_system'] = self.cif_data['_symmetry_cell_setting']

    def __iter__(self) -> dict:
        """
        An iterable for the Cif object
        :return: cif entries
        """
        if self.ok:
            yield self.cif_data
        else:
            yield {}

    def __hash__(self):
        return hash(self.cif_data)

    def __getattr__(self, item: str) -> str:
        """
        Returns an attribute of the cif data dictionary.
        """
        try:
            return self.cif_data[item]
        except KeyError:
            return ''

    def __str__(self) -> str:
        """
        The string representation for print(self)
        """
        out = ''
        for item in self.cif_data:
            if item == '_atom':
                out += "Atoms:         \t\t\t" + str(len(self.cif_data['_atom'])) + '\n'
                continue
            out += item + ':  \t' + "'" + str(self.cif_data[item]) + "'" + '\n'
        return out

    @property
    def cell(self) -> List[float]:
        """
        >>> cif = Cif()
        >>> ok = cif.parsefile(Cif.readfile(r'./test-data/COD/4060314.cif'))
        >>> cif.cell
        [12.092, 28.5736, 15.4221, 90.0, 107.365, 90.0]

        _cell_angle_alpha                90.0
        _cell_angle_beta                 107.365(1)
        _cell_angle_gamma                90.00
        _cell_formula_units_Z            4
        _cell_length_a                   12.0920(1)
        _cell_length_b                   28.5736(3)
        _cell_length_c                   15.4221(2)
        """
        a = self.cif_data['_cell_length_a']
        b = self.cif_data['_cell_length_b']
        c = self.cif_data['_cell_length_c']
        alpha = self.cif_data['_cell_angle_alpha']
        beta = self.cif_data['_cell_angle_beta']
        gamma = self.cif_data['_cell_angle_gamma']
        if not all((a, b, c, alpha, beta, gamma)):
            return []
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
        return [a, b, c, alpha, beta, gamma]

    @property
    def loops(self) -> List[Dict]:
        """
        >>> from searcher.fileparser import Cif
        >>> cif = Cif()
        >>> ok = cif.parsefile(Cif.readfile(r'./test-data/COD/4060314.cif'))
        >>> cif.loops[0]
        {'_publ_author_name': 'Eva Hevia'}
        """
        return self.cif_data['_loop']

    def loop_items(self, item: str) -> List[str]:
        """
        >>> cif = Cif()
        >>> ok = cif.parsefile(Cif.readfile(r'./test-data/COD/4060314.cif'))
        >>> cif.loop_items('_publ_author_name')
        ['Eva Hevia', 'Dolores Morales', 'Julio Perez', 'Victor Riera', 'Markus Seitz', 'Daniel Miguel']
        >>> ok = cif.parsefile(Cif.readfile(r'./test-data/ICSD/1923_Aminoff, G._Ni As_P 63.m m c_Nickel arsenide.cif'))
        >>> cif.loop_items('_symmetry_equiv_pos_site_id')
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
        """
        return [x[item] for x in self.loops if item in x]

    @property
    def atoms(self) -> List[Union[str, str, float, float, float, float, int]]:
        """
        A convenient way of getting atoms from the cif file
        [Name, type, x, y, z, occupancy, part]
        """
        for item in self._loop:
            try:
                name = item['_atom_site_label']
            except KeyError:
                continue
            try:
                try:
                    part = item['_atom_site_disorder_group']
                except KeyError:
                    part = 0
                try:
                    # The atom type
                    type_symbol = item['_atom_site_type_symbol']
                    if type_symbol not in sorted_atoms:
                        # For cases where type is not pure element name like Na1+:
                        type_symbol = self._atom_from_symbol(type_symbol)
                except KeyError:
                    label = item['_atom_site_label'].split('(')[0].capitalize()
                    # As last resort: cut out the atom type from the label
                    type_symbol = self._atom_from_symbol(label)
                try:
                    # The occupancy:
                    occu = float(item['_atom_site_occupancy'].split('(')[0])
                except (KeyError, ValueError):
                    # Better a wrong one than nothing:
                    occu = 1.0
                # The atom has at least a label and coordinates. Otherwise, no atom.
                x = item['_atom_site_fract_x']
                y = item['_atom_site_fract_y']
                z = item['_atom_site_fract_z']
                yield [name,
                       type_symbol,
                       float(0 if x == '.' else x.split('(')[0]),
                       float(0 if y == '.' else y.split('(')[0]),
                       float(0 if z == '.' else z.split('(')[0]),
                       occu,
                       0 if part == '.' or part == '?' else int(part)]
            except (KeyError, ValueError) as e:
                # print(e)
                # print(self.data)
                # raise
                continue

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
        >>> cif = Cif()
        >>> ok = cif.parsefile(Cif.readfile(r'./test-data/COD/4060314.cif'))
        >>> cif.symm
        ['x, y, z', '-x+1/2, y+1/2, -z+1/2', '-x, -y, -z', 'x-1/2, -y-1/2, z-1/2']
        """
        symm1 = self.loop_items('_space_group_symop_operation_xyz')
        symm2 = self.loop_items('_symmetry_equiv_pos_as_xyz')
        return symm1 if symm1 else symm2

    @staticmethod
    def readfile(file):
        with open(file, 'r') as f:
            return f.readlines()

    @staticmethod
    def delimit_line(line: str) -> List[str]:
        """
        Searches for delimiters in a cif line and returns a list of the respective values.
        >>> Cif.delimit_line("Aminoff, G.")
        ['Aminoff,', 'G.']
        >>> Cif.delimit_line("' x,y,z '")
        ['x,y,z']
        >>> Cif.delimit_line("'   +x,   +y,   +z'")
        ['+x, +y, +z']
        >>> Cif.delimit_line(" 'C'  'C'   0.0033   0.0016   'some text inside' \\"more text\\"")
        ['C', 'C', '0.0033', '0.0016', 'some text inside', 'more text']
        >>> Cif.delimit_line("123  123 sdf")
        ['123', '123', 'sdf']
        >>> Cif.delimit_line("'-2  34' '234'")
        ['-2 34', '234']
        >>> Cif.delimit_line("'x, y, z'")
        ['x, y, z']
        >>> Cif.delimit_line("'a dog's life'")
        ["a dog's life"]
        >>> Cif.delimit_line("'+x, +y, +z'")
        ['+x, +y, +z']
        >>> Cif.delimit_line("'-x, -y, -z'")
        ['-x, -y, -z']
        """
        data = []
        # remove space characters in front of characters behind ' or " and at the end
        line = line.lstrip().rstrip()
        if line.startswith("'") and line.endswith("'") or line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
            line = "'" + line.lstrip().rstrip() + "'"
        line = line.split(' ')
        word = []
        cont = False
        for i in line:
            if i:
                if i[0] == "'" or i[0] == '"':
                    if i[-1] == "'" or i[-1] == '"':
                        data.append(i.strip("'").strip('"'))
                        continue
                if i[0] == "'" or i[0] == '"':
                    word.clear()
                    word.append(i.strip("'").strip('"'))
                    cont = True
                    continue
                if i[-1] == "'" or i[-1] == '"':
                    word.append(i.strip("'").strip('"'))
                    data.append(' '.join(word))
                    cont = False
                    continue
                if cont:
                    word.append(i)
                else:
                    data.append(i)
        return data


if __name__ == '__main__':
    cif = Cif()
    cifok = cif.parsefile(Path(r'test-data/668839.cif').read_text().splitlines(keepends=True))
    # pprint(cif.cif_data)
    pprint(cif._space_group_centring_type)
    # sys.exit()
    # TODO: "_space_group_symop_operation_xyz" or '_symmetry_equiv_pos_as_xyz':
    for x in cif.atoms:
        pass
        print(x)
    print(cifok)
    import doctest

    failed, attempted = doctest.testmod()  # verbose=True)
    if failed == 0:
        print('passed all {} tests!'.format(attempted))
