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
import math

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

def find_binary_string(file, string, seek, size, return_ascii=False):
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
        position = binary.find(b'{0}'.format(string))
        if position > 0:
            f.seek(position+seek, 0) # seek to version string
            result = f.read(size)   # read version string
            if return_ascii:
                return result.decode('ascii')
            else:
                return result
            

def open_file_read(filename, asci=True):
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


def get_error_from_value(value: str) -> str:
    """ 
    Returns the error value from a number string.
    :TODO: Make exponents work "1.234e23"
    :type value: str
    :rtype: str
    >>> get_error_from_value("0.0123 (23)")
    '0.0023'
    >>> get_error_from_value("0.0123(23)")
    '0.0023'
    >>> get_error_from_value('0.0123')
    '0.0'
    >>> get_error_from_value("250.0123(23)")
    '0.0023'
    >>> get_error_from_value("123(25)")
    '25'
    """
    try:
        value = value.replace(" ", "")
    except AttributeError:
        return "0.0"
    if "(" in value and ")":
        val = value.split("(")[0].split('.')
        err = value.split("(")[1].split(")")[0]
        if len(val) > 1:
            return str(int(err) * (10 ** (-1 * len(val[1]))))
        else:
            return err
    else:
        return '0.0'


def flatten(lis):
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


def distance(x1, y1, z1, x2, y2, z2):
    """
    distance between two points in space for orthogonal axes.
    >>> distance(1, 1, 1, 2, 2, 2, 4)
    1.7321
    >>> distance(1, 0, 0, 2, 0, 0, 4)
    1.0
    """
    d = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
    return d


def format_sum_formula(sumform: str):
    """
    converts an atom name like C12 to the element symbol C
    Use this code to find the atoms while going through the character astream of a sumformula
    e.g. C12H6O3Mn7
    Find two-char atoms, them one-char, and see if numbers are in between.

    >>> format_sum_formula("C12H6O3Mn7")
    {'C': '12', 'H': '6', 'O': '3', 'Mn': '7'}
    >>> format_sum_formula("C12 H60 O3 Mn7")
    {'C': '12', 'H': '60', 'O': '3', 'Mn': '7'}
    >>> format_sum_formula("C12 H60 O3  Mn 7")
    {'C': '12', 'H': '60', 'O': '3', 'Mn': '7'}
    >>> format_sum_formula("C13Cs12 H60 O3  Mn 7")
    {'C': '13', 'Cs': '12', 'H': '60', 'O': '3', 'Mn': '7'}
    >>> format_sum_formula("CHMn\\n")
    {'C': '', 'H': '', 'Mn': ''}
    >>> format_sum_formula("Hallo")
    Traceback (most recent call last):
    ...
    KeyError

    >>> format_sum_formula('C4 H2.91 Al0.12 F4.36 Ni0.12 O0.48')
    {'C': '4', 'H': '2.91', 'Al': '0.12', 'F': '4.36', 'Ni': '0.12', 'O': '0.48'}
    >>> format_sum_formula('C4H6O1*5H2O')
    Traceback (most recent call last):
    ...
    KeyError

    """
    elements = [x.upper() for x in constants.atoms]
    atlist = {}
    nums = []
    sumform = sumform.upper().replace(' ', '').replace('\n', '')

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
            sumform = sumform[2+len(nums):]
            nums.clear()
        elif sumform[0] in elements:
            isnumber(sumform[1:])
            atlist[sumform[0]] = "".join(nums)
            sumform = sumform[1 + len(nums):]
            nums.clear()
        else:
            raise KeyError
    return atlist


