# -*- encoding: utf-8 -*-
# möpß
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <daniel.kratzert@ac.uni-freiburg.de> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
# Daniel Kratzert
# ----------------------------------------------------------------------------
#

"""
This file reads Bruker p4p files into a data structure.
"""


def read_file_to_list(self, resfile: str) -> list:
    """
    Read in shelx file and returns a list without line endings. +include files are inserted
    also.
    :param resfile: The path to a SHLEL .res or .ins file.
    """
    reslist = []
    includefiles = []
    try:
        with open(resfile, 'r') as f:
            reslist = f.read().splitlines(keepends=False)
    except (IOError) as e:
        print(e)
        print('*** CANNOT READ FILE {} ***'.format(resfile))
    return reslist