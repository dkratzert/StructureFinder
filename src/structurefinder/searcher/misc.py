"""
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <dkratzert@gmx.de> wrote this file. As long as you retain this
* notice you can do whatever you want with this stuff. If we meet some day, and
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

"""

import os
from math import cos, log, radians, sqrt
from pathlib import Path
from typing import Dict, List, Tuple, Union

from structurefinder.searcher import constants

COL_ID, COL_DATA, COL_FILE, COL_MODIFIED, COL_PATH = range(5)


def regular_results_parameters(volume):
    vol_threshold = log(volume) + 1.3
    ltol = 0.03
    atol = 1.0
    return atol, ltol, vol_threshold


def more_results_parameters(volume):
    vol_threshold = log(volume) + 20.0
    ltol = 0.05
    atol = 1.8
    return atol, ltol, vol_threshold


elements = ['X', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
            'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr',
            'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
            'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
            'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
            'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
            'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
            'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es']


def is_a_nonzero_file(filepath: Union[str, Path]) -> bool:
    """
    Check if a file exists and has some content.
    """
    if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:
        return True
    else:
        return False


def get_error_from_value(value: str) -> Tuple[float, float]:
    """
    Returns the error value from a number string.
    """
    try:
        value = value.replace(" ", "")
    except AttributeError:
        return float(value), 0.0
    if "(" in value:
        vval, err = value.split("(")
        val = vval.split('.')
        err = err.split(")")[0]
        if not err:  # for error given as ()
            err = 0.0
        if len(val) > 1:
            return float(vval), int(err) * (10 ** (-1 * len(val[1])))
        else:
            return float(vval), float(err)
    else:
        try:
            return float(value), 0.0
        except ValueError:
            return 0.0, 0.0


def get_value(string):
    """
    Returns only the numeric value from a cif item like 1.234(4).

    :parameters
        ** string **
            A cif value as string
    :returns
        The value without error. (`float`)
    """
    if "(" in string:
        vval, _ = string.split("(")
        if vval == '':
            vval = '0'
        return float(vval)
    else:
        return float(string)


def format_sum_formula(sumform: Dict[str, Union[int, float]], break_after: int = 99) -> str:
    """
    Makes html formated sum formula from dictionary.
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


def formula_dict_to_str(formula: Dict[str, Union[int, float]]) -> str:
    """
    Converts a sum formula from a dictionary like {'C': 12, 'H': 6, 'O': 3} to a
    string like C12 H6 O3

    >>> formula_dict_to_str({'Elem_C': 12, 'Elem_H': 6.5, 'Elem_O': 3, 'Elem_Mn': 7})
    'C12 H6.5 O3 Mn7'
    """
    formstr = ' '.join([x[5:] + str(formula[x]) for x in formula.keys()])
    return formstr


def formula_dict_to_elements(formula: Dict[str, int]) -> str:
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


def formula_str_to_dict(sumform: Union[str, bytes]) -> Dict[str, str]:
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


def get_list_of_elements(formula: str) -> Union[List[str], None]:
    """
    Get the list of elements from a formula.
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
            return None
    return atlist


def is_valid_cell(cell: str = None) -> List[float]:
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


def combine_results(cell_results: List,
                    date_results: List,
                    elincl_results: List,
                    results: Union[List, set],
                    spgr_results: List,
                    txt_ex_results: Union[List, Tuple],
                    txt_results: Union[List, Tuple],
                    rval_results: List, states: dict) -> Union[set, List]:
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


def vol_unitcell(a: float, b: float, c: float, al: float, be: float, ga: float) -> float:
    """
    calculates the volume of a unit cell

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
