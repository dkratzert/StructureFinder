'''
Created on 09.02.2015

searches cells in the db

-use http://pymatgen.org/index.html for niggli cell search

@author: daniel
'''
import sys

def cell_search(structures, cell_abc):
    a, b, c = None, None, None
    try:
        a = cell_abc[0]
    except:
        pass
    try:
        b = cell_abc[1]
    except:
        pass
    try:
        c = cell_abc[2]
    except:
        pass
    print('searching cell...')
    result = structures.find_cell_by_abc(a, b, c)
    if not result:
        print('No cell found!')
        sys.exit()
    print('Found the following files:')    
    for i in result:
        cell = i[2:]
        i = i[0]
        try:
            print('{1}: {0} \n\t {2}'.format(structures[i][0][0], 
                                         structures[i][0][1], cell))
        except:
            pass
    print('\n')


def big_cell_search(structures):
    print('########## Biggest cell #############')
    result = structures.find_biggest_cell()
    print(result)
    
    
    
    
    
