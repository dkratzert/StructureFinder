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
import shutil
from math import sqrt, cos, radians

from searcher import constants


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


elements = ['X', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
            'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr',
            'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
            'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
            'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
            'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
            'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
            'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es']


def write_file(list: list, name: str) -> None:
    """
    Writes the content of list to name.
    :param list: list
    :param name:  string
    """
    with open(name, 'w') as ofile:
        for line in list:  # modified reslist
            ofile.write("%s" % line)  # write the new file


def find_binary_string(file, string: str, seek, size, return_ascii=False):
    """
    finds a string in a binary file
    :rtype: str
    :param file: file path
    :param string: string to find
    :param seek: go number of bytes ahead
    :param size: return string of size
    :param return_ascii: return as ascii or not
    """
    with open(file, 'rb') as f:
        binary = f.read()
        position = binary.find(bytes(string))
        if position > 0:
            f.seek(position + seek, 0)  # seek to version string
            result = f.read(size)  # read version string
            if return_ascii:
                return result.decode('ascii')
            else:
                return result


def walkdir(rootdir, include=None, exclude=None):
    """
    Returns a list of files in all subdirectories with full path.
    :param rootdir: base path from which walk should start
    :param filter: list of file endings to include only e.g. ['.py', '.res']
    :return: list of files

    >>> walkdir("../setup/modpath.iss")
    ['../setup/modpath.iss']
    >>> walkdir("../setup/modpath.iss", exclude=['.iss'])
    []
    """
    if not include:
        include = ""
    if not exclude:
        exclude = ""
    results = []
    if not os.path.isdir(rootdir):
        if os.path.splitext(rootdir)[1] in exclude:
            return []
        return [rootdir]
    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            fullfilepath = os.path.join(root, file)
            if exclude:
                if os.path.splitext(fullfilepath)[1] in exclude:
                    continue
            if include:
                if os.path.splitext(fullfilepath)[1] in include:
                    results.append(os.path.normpath(fullfilepath).replace('\\', '/'))
            else:
                results.append(os.path.normpath(fullfilepath).replace('\\', '/'))
    return results


def open_file_read(filename: str, asci: bool = True) -> str or list:
    if asci:
        state = 'r'
    else:
        state = 'rb'
    with open(filename, '{0}'.format(state)) as f:
        if asci:
            try:
                file_list = f.readlines()
            except:
                return [' ']
            return file_list
        else:
            binary = f.read()
            return binary


def is_a_nonzero_file(filename):
    """
    Check if a file exists and has some content.

    >>> is_a_nonzero_file('./searcher/misc.py')
    True
    >>> is_a_nonzero_file('foo.bar')
    False
    >>> is_a_nonzero_file('./test-data/test_zerofile.cif')
    False
    >>> is_a_nonzero_file('./strf.py')
    True
    """
    filesize = False
    status = False
    if os.path.isfile(filename):
        filesize = int(os.stat(str(filename)).st_size)
    else:
        return False
    if isinstance(filesize, int) and filesize > 0:
        status = True
    if isinstance(filesize, int) and filesize == 0:
        status = False
    return status


def get_error_from_value(value: str) -> tuple:
    """
    Returns the error value from a number string.
    :type value: str
    :rtype: str
    >>> get_error_from_value("0.0123 (23)")
    (0.0123, 0.0023)
    >>> get_error_from_value("0.0123(23)")
    (0.0123, 0.0023)
    >>> get_error_from_value('0.0123')
    (0.0123, 0.0)
    >>> get_error_from_value("250.0123(23)")
    (250.0123, 0.0023)
    >>> get_error_from_value("123(25)")
    (123.0, 25.0)
    >>> get_error_from_value("123(25")
    (123.0, 25.0)
    """
    try:
        value = value.replace(" ", "")
    except AttributeError:
        return value, 0.0
    if "(" in value:
        vval, err = value.split("(")
        val = vval.split('.')
        err = err.split(")")[0]
        if len(val) > 1:
            return float(vval), int(err) * (10 ** (-1 * len(val[1])))
        else:
            return float(vval), float(err)
    else:
        try:
            return float(value), 0.0
        except ValueError:
            return 0.0, 0.0


def flatten(lis: list) -> list:
    """
    Given a list, possibly nested to any level, return it flattened.
    From: http://code.activestate.com/recipes/578948-flattening-an-arbitrarily-nested-list-in-python/
    """
    new_lis = []
    for item in lis:
        if type(item) == type([]):
            new_lis.extend(flatten(item))
        else:
            new_lis.append(item)
    return new_lis


def distance(x1: float, y1: float, z1: float,
             x2: float, y2: float, z2: float) -> float:
    """
    distance between two points in space for orthogonal axes.
    >>> distance(1, 1, 1, 2, 2, 2)
    1.7320508075688772
    >>> distance(1, 0, 0, 2, 0, 0)
    1.0
    """
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


def format_sum_formula(sumform: dict, break_after: int = 99) -> str:
    """
    Makes html formated sum formula from dictionary.
    >>> format_sum_formula({'C': 12, 'H': 6, 'O': 3, 'Mn': 7})
    '<html><body>C<sub>12 </sub>H<sub>6 </sub>O<sub>3 </sub>Mn<sub>7 </sub></body></html>'
    """
    # atlist = formula_str_to_dict(sumform)
    if not sumform:
        return ''
    l = ['<html><body>']
    num = 0
    for i in sumform:
        if i == 'Id' or i == 'StructureId':
            continue
        if sumform[i] == 0 or sumform[i] == None:
            continue
        try:
            times = round(sumform[i], 1)
        except TypeError:
            times = 1
        if num > 3 and num % break_after == 0:
            l.append("<br>")
        try:
            el = i.split('_')[1]  # split here, because database returns 'Elem_C' for example
        except IndexError:
            el = i
        l.append("{}<sub>{:g} </sub>".format(el, times))
        num += 1
    l.append('</body></html>')
    formula = "".join(l)
    # print(formula)
    return formula


def formula_dict_to_str(formula: dict):
    """
    Converts a sum formula from a dictionary like {'C': 12, 'H': 6, 'O': 3} to a
    string like C12 H6 O3

    >>> formula_dict_to_str({'Elem_C': 12, 'Elem_H': 6.5, 'Elem_O': 3, 'Elem_Mn': 7})
    'C12 H6.5 O3 Mn7'
    """
    formstr = ' '.join([x[5:] + str(formula[x]) for x in formula.keys()])
    return formstr


def formula_dict_to_elements(formula: dict):
    """
    Converts a sum formula from a dictionary like {'C': 12, 'H': 6, 'O': 3} to a
    string like C H O.
    >>> formula_dict_to_elements({'Elem_C': 12, 'Elem_H': 6.5, 'Elem_O': 3, 'Elem_Mn': 7})
    'C H O Mn'
    >>> formula_dict_to_elements({'Elem_C': 12, 'Elem_H': 6.5, 'Elem_O': 3, 'Elem_Mn': 7, 'Elem_N': 0})
    'C H O Mn'
    """
    formstr = ' '.join([x[5:] for x in formula.keys() if formula[x]])
    return formstr


def formula_str_to_dict(sumform: str or bytes) -> dict:
    """
    converts an atom name like C12 to the element symbol C
    Use this code to find the atoms while going through the character astream of a sumformula
    e.g. C12H6O3Mn7
    Find two-char atoms, them one-char, and see if numbers are in between.

    >>> formula_str_to_dict("SSn")
    {'S': '', 'Sn': ''}
    >>> formula_str_to_dict("S1Cl")
    {'S': '1', 'Cl': ''}
    >>> formula_str_to_dict("C12H6O3Mn7")
    {'C': '12', 'H': '6', 'O': '3', 'Mn': '7'}
    >>> formula_str_to_dict("C12 H60 O3 Mn7")
    {'C': '12', 'H': '60', 'O': '3', 'Mn': '7'}
    >>> formula_str_to_dict("C12 H60 O3  Mn 7")
    {'C': '12', 'H': '60', 'O': '3', 'Mn': '7'}
    >>> formula_str_to_dict("C13Cs12 H60 O3  Mn 7")
    {'C': '13', 'Cs': '12', 'H': '60', 'O': '3', 'Mn': '7'}
    >>> formula_str_to_dict("CHMn\\n")
    {'C': '', 'H': '', 'Mn': ''}
    >>> formula_str_to_dict("Hallo")
    Traceback (most recent call last):
    ...
    KeyError

    >>> formula_str_to_dict('C4 H2.91 Al0.12 F4.36 Ni0.12 O0.48')
    {'C': '4', 'H': '2.91', 'Al': '0.12', 'F': '4.36', 'Ni': '0.12', 'O': '0.48'}
    >>> formula_str_to_dict('C4H6O1*5H2O')
    Traceback (most recent call last):
    ...
    KeyError

    """
    elements = [x.upper() for x in constants.atoms]
    atlist = {}
    nums = []
    try:
        sumform = sumform.upper().replace(' ', '').replace('\n', '').replace('\r', '')
    except AttributeError:
        print('Error in formula_str_to_dict')
        return atlist

    def isnumber(el):
        for x in el:
            if x.isnumeric() or x == '.':
                nums.append(x)
            else:
                # end of number
                break

    while sumform:
        if sumform[0:2] in elements:  # The two-character elements
            isnumber(sumform[2:])
            atlist[sumform[0:2].capitalize()] = "".join(nums)
            sumform = sumform[2 + len(nums):]
            nums.clear()
        elif sumform[0] in elements:
            isnumber(sumform[1:])
            atlist[sumform[0]] = "".join(nums)
            sumform = sumform[1 + len(nums):]
            nums.clear()
        else:
            raise KeyError
    return atlist


def get_list_of_elements(formula: str) -> list:
    """
    >>> get_list_of_elements("SCl")
    ['S', 'Cl']
    >>> get_list_of_elements("S1Cl1")
    ['S', 'Cl']
    >>> get_list_of_elements("S1Cl")
    ['S', 'Cl']
    >>> get_list_of_elements("ScCl")
    ['Sc', 'Cl']
    >>> get_list_of_elements("S20 Cl")
    ['S', 'Cl']
    """
    elements = constants.atoms
    atlist = []
    formula = ''.join([i for i in formula if not i.isdigit()]).replace(' ', '')
    while formula:
        if formula[0:2] in elements:
            atlist.append(formula[0:2].capitalize())
            formula = formula[2:]
        elif formula[0:1] in elements:
            atlist.append(formula[0:1].capitalize())
            formula = formula[1:]
        else:
            raise KeyError
    return atlist


def remove_file(filename):
    """
    removes the file "filename" from disk
    >>> remove_file('foobar')
    True
    """
    if os.path.isfile(filename):
        try:
            os.remove(filename)
        except(IOError, OSError):
            print('Can not delete {}'.format(filename))
            return False
    return True


def copy_file(source, target, move=False):
    """
    Copy a file from source to target. Source can be a single file or
    a directory. Target can be a single file or a directory.
    :param source: list or string
    :param target: string
    """
    target_path = os.path.dirname(target)
    source_file = os.path.basename(source)
    listcopy = False
    if isinstance(source, (list, tuple)):
        listcopy = True
    if not os.path.exists(target_path) and target_path != '':
        try:
            os.makedirs(target_path)
        except(IOError, OSError):
            print('Unable to create directory {}.'.format(target_path))
    try:
        if listcopy:
            for filen in source:
                if move:
                    shutil.move(filen, target)
                else:
                    shutil.copy(filen, target)

        else:
            if move:
                shutil.move(source, target)
            else:
                shutil.copy(source, target)
    except IOError as e:
        print('Unable to copy {}.'.format(source_file))
        print(e)


def is_valid_cell(cell: str = None) -> list:
    """
    Checks is a unit cell is valid
    """
    if not cell:
        return []
    try:
        cell = [float(x) for x in cell.strip().split()]
    except (TypeError, ValueError):
        return []
    if len(cell) != 6:
        return []
    return cell


def combine_results(cell_results, date_results, elincl_results, results, spgr_results,
                    txt_ex_results, txt_results, rval_results: float, states: dict) -> set:
    """
    Combines all search results together. Returns a list with database ids from found structures.
    """
    if states['cell']:
        results.extend(cell_results)
    if states['spgr']:
        spgr_results = set(spgr_results)
        if results:
            results = set(results).intersection(spgr_results)
        else:
            if states['cell']:
                results = set([])
            else:
                results = spgr_results
    if states['elincl'] or states['elexcl']:
        elincl_results = set(elincl_results)
        if results:
            results = set(results).intersection(elincl_results)
        else:
            if states['spgr'] or states['cell']:
                results = set([])
            else:
                results = elincl_results
    if states['txt']:
        txt_results = set(txt_results)
        if results:
            results = set(results).intersection(txt_results)
        else:
            if states['elincl'] or states['spgr'] or states['cell']:
                results = set([])
            else:
                results = txt_results
    if states['txt_ex']:
        txt_ex_results = set(txt_ex_results)
        results = set(results) - set(txt_ex_results)
    if states['date']:
        date_results = set(date_results)
        if results:
            results = set(results).intersection(date_results)
        else:  # no results from other searches:
            if states['txt'] or states['elincl'] or states['spgr'] or states['cell']:
                results = set([])
            else:
                results = date_results
    if states['rval']:
        rval_results = set(rval_results)
        if results:
            results = set(results).intersection(rval_results)
        else:
            if states['txt'] or states['elincl'] or states['spgr'] or states['cell'] or states['date']:
                results = set([])
            else:
                results = rval_results
    return results


def vol_unitcell(a, b, c, al, be, ga):
    """
    calculates the volume of a unit cell
    :type a: float
    :type b: float
    :type c: float
    :type al: float
    :type be: float
    :type ga: float

    >>> v = vol_unitcell(2, 2, 2, 90, 90, 90)
    >>> print(v)
    8.0

    """
    # ca, cb, cg = cos(radians(al)), cos(radians(be)), cos(radians(ga))
    v = a * b * c * sqrt(1 + 2 * cos(radians(al)) * cos(radians(be)) * cos(radians(ga))
                         - cos(radians(al)) ** 2 - cos(radians(be)) ** 2 - cos(radians(ga)) ** 2)
    return v


if __name__ == '__main__':
    pass
