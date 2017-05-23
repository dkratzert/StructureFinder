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
import sys

import CifFile
from searcher import misc
from searcher.misc import get_error_from_value

essential_fields = ('_cell_length_a', '_cell_length_b', '_cell_length_c', '_cell_angle_alpha', '_cell_angle_beta',
                         '_cell_angle_gamma')
fields = ('_diffrn_ambient_temperature', '_diffrn_reflns_av_R_equivalents', '_diffrn_reflns_av_unetI/netI',
               '_diffrn_reflns_theta_max')

def get_cif_datablocks(filename):
    """
    returns the data objects in a cif file 
    """
    cif = CifFile.ReadCif(filename)
    return cif.visible_keys


def get_cif_cell_raw(filename):
    """
    Get the cell of a cif file
    _cell_length_a                    29.227(4)
    _cell_length_b                    6.6568(8)
    _cell_length_c                    11.8204(14)
    _cell_angle_alpha                 90
    _cell_angle_beta                  107.055(5)
    _cell_angle_gamma                 90
    and the respective error values
    ...
    _shelx_hkl_file
    ;
    hkl data
    ;
    Attention: This implementation currently uses only the first cell of a cif file
    
    - list of desired fileds
    - cifdict = {}
    for line in f:
        for f in fields:
            test = line[:len(f)]
            if test == f:
                cifdict[f] = test 
    
    """
    name, a, b, c, alpha, beta, gamma, esda, esdb, esdc, esdalpha, esdbeta, esdgamma = \
        None, None, None, None, None, None, None, None, None, None, None, None, None
    filename = os.path.abspath(filename.name)
    cell = [None,  # 0 name
            None,  # 1 a
            None,  # 2 b
            None,  # 3 c
            None,  # 4 alpha
            None,  # 5 beta
            None,  # 6 gamma
            None,  # 7 esda
            None,  # 8 esdb
            None,  # 9 esdc
            None,  # 10 esdalpha
            None,  # 11 esdbeta
            None]  # 12 esdgamma
    with codecs.open(filename, "r", encoding='ascii', errors='ignore') as f:
        for line in f:
            if line.startswith('data_'):
                name = line.split('_')[1].strip('\n')
                cell[0] = name
            if line.startswith('_cell_length_a'):
                a = line.split()[1].split('(')[0]
                cell[1] = float(a)
                cell[7] = get_error_from_value(a)
            if line.startswith('_cell_length_b'):
                b = line.split()[1].split('(')[0]
                cell[2] = float(b)
                cell[8] = get_error_from_value(b)
            if line.startswith('_cell_length_c'):
                c = line.split()[1].split('(')[0]
                cell[3] = float(c)
                cell[9] = get_error_from_value(c)
            if line.startswith('_cell_angle_alpha'):
                alpha = line.split()[1].split('(')[0]
                cell[4] = float(alpha)
                cell[10] = get_error_from_value(alpha)
            if line.startswith('_cell_angle_beta'):
                beta = line.split()[1].split('(')[0]
                cell[5] = float(beta)
                cell[11] = get_error_from_value(beta)
            if line.startswith('_cell_angle_gamma'):
                gamma = line.split()[1].split('(')[0]
                cell[6] = float(gamma)
                cell[12] = get_error_from_value(gamma)
            #if line.startswith("_shelx_hkl_file"):
            #    return cell
            if all(cell[n] for n, i in enumerate(cell)):
                # contains 1+n cells. n=0-inf
                return cell
    return []


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
        self.essential_fields = essential_fields
        self.fields = fields
        self.all_fields = self.essential_fields + self.fields
        self.ok = self.parsefile(file)

    def parsefile(self, file):
        data = False
        loophead = []
        loop = False
        loopdata = []
        atoms = {}
        with codecs.open(file, "r", encoding='ascii', errors='ignore') as f:
            for num, line in enumerate(f):
                loop = False  # for testing
                if loop:
                    l = line.lstrip().strip('\r\n ')
                    if not l.strip():
                        loop = False
                        loophead.clear()
                        loopdata.clear()
                        continue
                    if l[:1] == "_":
                        loophead.append(l)
                    else:
                        loopitem = {}
                        datline = l.split()
                        # quick hack, have to unwrap lines:
                        if len(datline) != len(loophead):
                            print(loopdata)
                            continue
                        for n, item in enumerate(datline):
                            loopitem[loophead[n]] = item
                        # TODO: Add every item of the loops to a specific dict e.g. _atom
                        # and structure the above loop with methods
                        loopdata.append(loopitem)
                        #print(loopdata)
                # First find the start of the cif (the data tag)
                if line.startswith('data_') and not data:
                    name = line.split('_')[1].strip('\n\r')
                    self.cif_data['data'] = name
                    data = True
                    continue
                if line.startswith('data_') and data:
                    break  # TODO: support multi cif
                # Find the loop positions:
                if line[:5] == "loop_":
                    loop = True
                    continue
                for x in self.all_fields:  # TODO: has to be more general
                    test = line[:len(x)]
                    if test == x:
                        self.cif_data[x] = line.split()[1]
                        continue
                if line.startswith("_shelx_hkl_file"):
                    break
        for fi in self.essential_fields:
            try:
                self.cif_data[fi]
            except KeyError:
                return False
        return True

    def __iter__(self):
        """
        an iterable for the Cif object
        :return: cif entries
        """
        if self.ok:
            yield self.cif_data
        else:
            return False

    #@property
    #def cell_a(self):
    #    a = self.cif_data['_cell_length_a']
    #    a = a.split()[1].split('(')[0]
    #    a = float(a)
    #    return a, get_error_from_value(a)


def get_cif_cell(filename):
    """
    parses cif files with pyCifRW. This is dead slow.
    """
    try:
        cif = CifFile.ReadCif(filename)
    except (CifFile.StarFile.StarError, UnicodeDecodeError):
        print("Could not parse cif file...")
        return []
    try:
        data = cif.visible_keys[0]
    except AttributeError:
        print("Could not parse cif file....")
        return []
    a = cif[data].get('_cell_length_a')
    b = cif[data].get('_cell_length_b')
    c = cif[data].get('_cell_length_c')
    alpha = cif[data].get('_cell_angle_alpha')
    beta = cif[data].get('_cell_angle_beta')
    gamma = cif[data].get('_cell_angle_gamma')
    esda = get_error_from_value(a)
    esdb = get_error_from_value(b)
    esdc = get_error_from_value(c)
    esdalpha = get_error_from_value(alpha)
    esdbeta = get_error_from_value(beta)
    esdgamma = get_error_from_value(gamma)
    try:
        a = a.split("(")[0].strip()
        b = b.split("(")[0].strip()
        c = c.split("(")[0].strip()
        alpha = alpha.split("(")[0].strip()
        beta = beta.split("(")[0].strip()
        gamma = gamma.split("(")[0].strip()
    except AttributeError:
        pass
    return [data, a, b, c, alpha, beta, gamma, esda, esdb, esdc, esdalpha, esdbeta, esdgamma]


def get_res_cell(filename):
    """
    Returns the unit cell parameters from the list file as list:
    ['a', 'b', 'c', 'alpha', 'beta', 'gamma']
    """
    file_list = misc.open_file_read(filename)
    cell = False
    for line in file_list:
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
        #print('Unable to find unit cell parameters in the file.')
        return False
    return cell


if __name__ == '__main__':

    c = Cif("../test-data/p21c.cif")
    for i in c:
        print(i)