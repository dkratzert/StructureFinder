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
import fnmatch as fn
import sys
from pathlib import Path
from pprint import pprint


def create_file_list(searchpath='None', endings='cif'):
    """
    walks through the file system and collects cells from res/cif files
    into a database
    """
    if not os.path.isdir(searchpath):
        print('search path {0} not found!'.format(searchpath))
        sys.exit()
    print('collecting files...')
    res = filewalker(searchpath)
    print('ready')
    return res


def filewalker(startdir, endings="*.cif"):
    """
    file walker with pathlib
    :param startdir: 
    :param endings: 
    :return:
     
    #>>> filewalker3('../')
    """
    p = Path(startdir)
    paths = p.rglob("*.cif")
    return paths


def filewalker_walk(startdir, endings, add_excludes=[]):
    """
    walks through the filesystem starting from startdir and searches
    for files with ending endings.
    """
    filelist = []
    excludes = ['.olex', 'dsrsaves']
    if add_excludes:
        excludes.extend(add_excludes)
    print('collecting files below ' + startdir)
    for root, dirs, files in os.walk(startdir):  # @UnusedVariable
        for num, filen in enumerate(files):
            if fn.fnmatch(filen, '*.{0}'.format(endings)):
                if os.stat(os.path.join(root, filen)).st_size == 0:
                    continue
                filelist.append([os.path.join(root, filen), filen])
            else:
                continue
            # TODO:
            #if num%100:
            #    return filelist
    return filelist


    


if __name__ == '__main__':
    res = filewalker('D:\\', 'res')
    for i in res:
        print(i)
    #print(res)
    #print(cif)