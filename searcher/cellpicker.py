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

import CifFile
from searcher import misc


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
    ...
    _shelx_hkl_file
    ;
    hkl data
    ;
    """
    # list of 1+n cells, because we can have more than one cif in a file. n = 0-inf:
    cells = []
    name, a, b, c, alpha, beta, gamma, esda, esdb, esdc, esdalpha, esdbeta, esdgamma = \
        None, None, None, None, None, None, None, None, None, None, None, None, None
    filename = os.path.abspath(filename.name)
    with open(filename) as f:
        with codecs.open(filename, "r", encoding='ascii', errors='ignore') as f:
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
    return cell
                #if all(cell[n] for n, i in enumerate(cell)):
                #    # contains 1+n cells. n=0-inf
                #    cells.append(cell[:])
                #    cell = [None, None, None, None, None, None, None, None, None, None, None, None]
    #return cells

def get_cif_cell(filename):
    """
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


def get_error_from_value(value):
    """ 
    :type value: str
    >>> get_error_from_value("0.0123 (23)")
    '0.0023'
    >>> get_error_from_value("0.0123(23)")
    '0.0023'
    >>> get_error_from_value('0.0123')
    '0.0'
    """
    try:
        value = value.replace(" ", "")
    except AttributeError:
        return "0.0"
    if "(" in value:
        spl = value.split("(")
        val = spl[0].split('.')
        err = spl[1].strip(")")
        return val[0]+"."+"0"*(len(val[1])-len(err))+err
    else:
        return '0.0'

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
    cells = get_cif_cell('c:/temp/c2c_final.cif')
    cellres = get_res_cell('c:/temp/c2c.res')
    for i in cells:
        print(i)
    print(cellres)