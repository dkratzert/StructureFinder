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

import CifFile
from searcher import misc


def get_cif_datablocks(filename):
    """
    returns the data objects in a cif file 
    """
    cif = CifFile.ReadCif(filename)
    return cif.visible_keys

def get_cif_cell(filename):
    """
    """
    try:
        cif = CifFile.ReadCif(filename)
    except CifFile.StarFile.StarError:
        return []
    data = cif.visible_keys[0]
    a = cif[data].get('_cell_length_a')
    b = cif[data].get('_cell_length_b')
    c = cif[data].get('_cell_length_c')
    alpha = cif[data].get('_cell_length_alpha')
    beta = cif[data].get('_cell_length_beta')
    gamma = cif[data].get('_cell_length_gamma')
    return [data, a, b, c, alpha, beta, gamma]



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