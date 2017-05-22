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

def find_binary_string(self, file, string, seek, size, return_ascii=False):
    '''
    finds a string in a binary file
    :param file: filpath
    :param string: string to find
    :param seek: go number of bytes ahead
    :param size: return string of size
    :param return_ascii: return as ascii or not
    '''
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
        if len(val) > 0:
            return "0"+"."+"0"*(len(val[1])-len(err))+err
        else:
            return err
    else:
        return '0.0'