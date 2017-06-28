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


def get_error_from_value(value: str) -> object:
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
    if "(" in value:
        spl = value.split("(")
        val = spl[0].split('.')
        err = spl[1].strip(")")
        if len(val) > 1:
            return str(int(err) * (10 ** (-1* len(val[1]))))
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
    import math as m
    d = m.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
    return d