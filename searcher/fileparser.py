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
import codecs
import os
import time
from pprint import pprint

import sys

import re

from searcher import misc
from searcher.misc import get_error_from_value


class Cif():
    def __init__(self, file):
        """
        A cif file parsing object optimized for speed and simplicity.
        :param file: input filename object
        :type file: object

        - find loops
          - get loop header
          - start and end
        - fill for example atom loop dict with atoms
        """
        self.cif_data = {}
        self.ok = self.parsefile(file)

    def parsefile(self, file):
        """
        This method parses the cif file. Currently, only single items and atoms are supported.
        TODO: Implement multi line comments ";"
        TODO: Implement line breaks in values

        :param file: Cif file name
        :type file: Path
        :return: cif file content
        :rtype: dict
        """
        data = False
        loop = False
        hkl = False
        loophead_list = []
        save_frame = False
        atoms = {}
        atkey = ''
        num = 0
        semi_colon_text_field = ''
        semi_colon_text_list = []
        cont = False  # continue to next line if True
        with file.open(mode='r', encoding='ascii', errors="ignore") as f:
            txt = f.readlines()
            textlen = len(txt)
            for num, line in enumerate(txt):
                line = line.rstrip('\r\n ')
                if loop:
                    if not line:
                        loop = False
                        loophead_list.clear()
                        atkey = ''
                        continue
                    line = line.lstrip()
                    # leave out comments:
                    if line[0] == '#':
                        continue
                    # Leave out save_ frames:
                    if save_frame:
                        continue
                    if line[:5] == "save_":
                        save_frame = True
                        continue
                    elif line[:5] == "save_" and save_frame:
                        save_frame = False
                    # to collect the two parts of an atom loop (have to do it more general):
                    if line == '_atom_site_label':
                        atkey = '_atom_site_label'
                    if line == '_atom_site_aniso_label':
                        atkey = '_atom_site_aniso_label'
                    #if line == "_atom_type_symbol":
                    #    atkey = "_atom_type_symbol"
                    #if line == "_atom_type_scat_dispersion_real":
                    #    atkey = "_atom_type_scat_dispersion_real"
                    #if line == "_atom_type_scat_dispersion_imag":
                    #    atkey = "_atom_type_scat_dispersion_imag"
                    #if line == "_atom_type_scat_source":
                        atkey = "_atom_type_scat_source"
                    # collecting keywords from head:
                    if line[:1] == "_":
                        loophead_list.append(line)
                        continue
                    # We are in a loop and the header ended, so we collect data:
                    else:
                        loopitem = {}
                        loop_data_line = delimit_line(line)
                        # unwrap loop data:
                        if len(loop_data_line) != len(loophead_list):
                            if textlen - 1 > num:
                                loop_data_line.extend(delimit_line(txt[num + 1]))
                            continue
                        for n, item in enumerate(loop_data_line):
                            loopitem[loophead_list[n]] = item
                        # TODO: make this general. Not only for atoms:
                        if atkey and loopitem[atkey] in atoms:
                            # atom is already there not there, upating values
                            atoms[loopitem[atkey]].update(loopitem)
                        elif atkey:
                            # atom is not there, creating key
                            atoms[loopitem[atkey]] = loopitem
                # First find the start of the cif (the data tag)
                if line[:5] == 'data_':
                    if not data:
                        name = line.split('_')[1].strip('\n\r')
                        self.cif_data['data'] = name
                        data = True
                        continue
                    else:
                        break  # TODO: support multi cif
                # Find the loop positions:
                if line[:5] == "loop_":
                    loop = True
                    continue
                # Collect all data items outside loops:
                if line.startswith('_') and not loop:
                    lsplit = line.split()
                    if len(lsplit) > 1:
                        self.cif_data[lsplit[0]] = " ".join(delimit_line(" ".join(lsplit[1:])))
                if line.startswith("_shelx_hkl_file") or line.startswith("_refln_"):
                    hkl = True
                    continue
                # Leave out hkl frames:
                if hkl:
                    break
                    # continue  # use continue if data is behind hkl
                if line.lstrip()[:1] == ";" and hkl:
                    hkl = False
                if semi_colon_text_field:
                    if not line.lstrip().startswith(";"):
                        semi_colon_text_list.append(line)
                    if (textlen - 1 > num) and txt[num + 1][0] == ";":
                        self.cif_data[semi_colon_text_field] = "{}".format(os.linesep).join(semi_colon_text_list)
                        semi_colon_text_list.clear()
                        semi_colon_text_field = ''
                        continue
                if (textlen - 1 > num) and txt[num + 1][0] == ";":
                    if line.startswith("_shelx_res_file"):
                        break
                        # continue  # use continue if data is behind res file
                    semi_colon_text_field = line
                    continue
        self.cif_data['_atom'] = atoms
        self.cif_data['file_length_lines'] = num+1
        # pprint(self.cif_data)  # slow
        if not data:
            return False
        if not atoms:
            self.cif_data.clear()
            return False
        else:
            return True

    def __iter__(self):
        """
        an iterable for the Cif object
        :return: cif entries
        """
        if self.ok:
            yield self.cif_data
        else:
            yield {}

    def __hash__(self):
        return hash(self.cif_data)

    def __getattr__(self, item):
        """ 
        Returns an attribute of the cif data dictionary.
        """
        if item in self.cif_data:
            return self.cif_data[item]
        else:
            return ''

    def __str__(self):
        """ 
        The string representation for print(self)
        """
        out = ''
        for item in self.cif_data:
            if item == '_atom':
                out += "Atoms:         \t\t\t"+str(len(self.cif_data['_atom']))+'\n'
                continue
            out += item+':  \t'+"'"+str(self.cif_data[item])+"'"+'\n'
        return out


def delimit_line(line):
    """
    Searches for delimiters in a cif line and returns a list of the respective values.
    >>> line = " 'C'  'C'   0.0033   0.0016   'some text inside' \\"more text\\""
    >>> delimit_line(line)
    ['C', 'C', '0.0033', '0.0016', 'some text inside', 'more text']
    >>> delimit_line("123  123 sdf")
    ['123', '123', 'sdf']
    >>> delimit_line("'-2  34' '234'")
    ['-2 34', '234']
    >>> delimit_line("'x, y, z'")
    ['x, y, z']
    
    :param line:
    :type line: str
    :return: list of values
    :rtype: list
    """
    data = []
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


def get_res_cell(filename):
    """
    Returns the unit cell parameters from the list file as list:
    ['a', 'b', 'c', 'alpha', 'beta', 'gamma']
    """
    cell = False
    with filename.open(mode='r', encoding='ascii', errors="ignore") as f:
        for line in f:
            if line[:4] == 'CELL':
                cell = line.split()[2:8]
                try:
                    cell = [float(i) for i in cell]
                    if not len(cell) == 6:
                        raise ValueError
                except ValueError:
                    print('Bad cell parameters in {0}.'.format(filename))
                    return False
                if line[:4] == 'UNIT':
                    break
    if not cell:
        # Unable to find unit cell parameters in the file.
        return False
    return cell


if __name__ == '__main__':
    import doctest
    failed, attempted = doctest.testmod()  # verbose=True)
    if failed == 0:
        print('passed all {} tests!'.format(attempted))
    from pathlib import Path
    time1 = time.clock()
    cif = "./test-data/p21c.cif"
    #cif = "/Users/daniel/.olex2/data/3e30b45376c2d4175951f811f7137870/customisation/cif_templates/ALS_BL1131_post_07_2014.cif"
    #cif = "/Users/daniel/Documents/Strukturen/DK_ML7-66/DK_ML7-66-final-old.cif"
    #cif = "/Users/daniel/Downloads/.olex/originals/10000007.cif"
    c = Cif(Path(cif))
    time2 = time.clock()
    diff = round(time2-time1, 4)
    #print(c.cif_data["_space_group_name_H-M_alt"])
    #sys.exit()
    #for i in c:
     #   pass
      #  pprint(i)
        #for x in i:
        #    print(x), print(i[x])
    print('-'*50)
    #print(c._shelx_space_group_comment, '##')
    #print(c._atom.keys(), '##')
    print(c)
    print('-' * 50)
    print(diff, 's')