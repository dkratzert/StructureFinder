'''
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <daniel.kratzert@uni-freiburg.de> wrote this file. As long as you retain this 
* notice you can do whatever you want with this stuff. If we meet some day, and 
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: daniel
'''

import os
import fnmatch as fn
from searcher.cellpicker import get_res_cell
import sys


def create_file_list(searchpath='None', endings='res'):
    '''
    walks through the file system and collects cells from res/cif files
    into a database
    '''
    if not os.path.isdir(searchpath):
        print('search path {0} not found!'.format(searchpath))
        sys.exit()
    print('collecting files...')
    res = filewalker(searchpath, endings)
    print('ready')
    return res

    
def filewalker(startdir, endings, add_excludes=[]):
    '''
    walks through the filesystem starting from startdir and searches
    for files with ending endings.
    '''
    filelist = []
    excludes = ['.olex', 'dsrsaves']
    if add_excludes:
        excludes.append(add_excludes)
    print('collecting files below '+startdir)
    for root, dirs, files in os.walk(startdir):  # @UnusedVariable
        for filen in files:
            if fn.fnmatch(filen, '*.{0}'.format(endings)):
                if os.stat(os.path.join(root, filen)).st_size == 0:
                    continue
                filelist.append([root, filen])
            else:
                continue
    return filelist


def create_cells_table(structures):
    print('filling cells into table...')
    num = 0
    numgut = 0
    for n in range(1, len(structures)):
        path = structures[n][0][0]
        name = structures[n][0][1]
        cell = get_res_cell(os.path.join(path, name))
        if not cell:
            num = num+1 
            cell = [0.1, 0.1, 0.1, 90, 90, 90]  # dummy cell
        else:
            numgut = numgut+1
        structures.fill_cell_table(n, cell)
    if num > 0: 
        print('{0} res files with invalid unit cells were found.'.format(num))
        print('-> xd2006 .res files also count to the invalid unit cells.')
    print('{0} res files with correct unit cells were found.'.format(numgut))
    print('ready!')
    print('Now you search in your database.')
    


if __name__ == '__main__':
    res = filewalker('c:\\Temp', 'res')
    for i in res:
        print(i)
    #print(res)
    #print(cif)