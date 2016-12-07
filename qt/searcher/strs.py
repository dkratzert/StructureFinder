#!/usr/local/bin/python2.7
# encoding: utf-8

'''
 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <daniel.kratzert@uni-freiburg.de> wrote this file. As long as you retain this 
* notice you can do whatever you want with this stuff. If we meet some day, and 
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author:     Daniel Kratzert

@copyright:  2015 Albert-Ludwigs-University of Freiburg. All rights reserved.

@license:    Beerware

@contact:    dkratzert@gmx.de    
@deffield    updated: 
'''

import sys
import os

req_version = (2,5)
cur_version = sys.version_info

try:
    if cur_version < req_version:
        print("Your Python interpreter is too old (version {0}.{1}.{2}) \
                Please consider upgrading.").format(cur_version[0], cur_version[1], cur_version[2]) 
        sys.exit()
except:
    print("Your Python interpreter is too old. Please consider upgrading.")
    sys.exit()
    
from database_handler import DatabaseRequest, StructureTable
from filecrawler import create_cells_table, create_file_list
import optparse
try:
    from argparse import ArgumentParser
    optparse = False
except:
    from optparse import OptionParser
    optparse = True
from searchhandler import cell_search, big_cell_search
import logging

VERSION = 1

################################################################################
if not optparse:
    parser = ArgumentParser(description=('This program searches for unit cells in \
                                        res files in the file system tree.\n\
                                        First create a database with -c and -p, \
                                        then search with -d and -s.'))
    parser.add_argument("-s", dest="cell_abc", 
                    default=False,
                    nargs='+',
                    metavar='cellparam', help=("Search for \
                    either one, two or all three cell edges together. e.g. 10.02 6.123"))

    parser.add_argument("-d", dest="db_input", 
                    metavar='database path', 
                    default=False,
                    help="Path were the cell database is located. You need this \
                    parameter to search for unit cells. \n\
                    ------------------- Create Database: -----------------")
                    
    parser.add_argument('-c', dest="createdb", 
                    metavar='database path', 
                    default=False,
                    help=r"Database name and path. E.g. c:\tmp\celldb.sqlite or /home/user/celldb.sql")

    parser.add_argument("-p", dest="searchpath", 
                    metavar='search path', 
                    default=False,
                    help="Path were strs searches for res files To build the \
                    database.")
    opt = parser.parse_args()
else:
    def cb(option, opt_str, value, parser):
        args=[]
        for arg in parser.rargs:
                if arg[0] != "-":
                        args.append(arg)
                else:
                        del parser.rargs[:len(args)]
                        break
        if getattr(parser.values, option.dest):
                args.extend(getattr(parser.values, option.dest))
        setattr(parser.values, option.dest, args)
        
    parser = OptionParser(description=('This program searches for unit cells in \
                                        res files in the file system tree.\n\
                                        First create a database with -c and -p, \
                                        then search with -d and -s.'))
    parser.add_option("-s", dest="cell_abc", 
                    default=False,
                    action="callback", callback=cb,
                    #nargs=[1,3],
                    metavar='cellparam', help=("Search for \
                    either one, two or all three cell edges together. e.g. 10.02 6.123"))
    
    parser.add_option("-d", dest="db_input", 
                    metavar='database path', 
                    default=False,
                    help="Path were the cell database is located. You need this \
                    parameter to search for unit cells.\
                    ------------------------------------")
    parser.add_option('-c', dest="createdb", 
                    metavar='database path', 
                    default=False,
                    help=r"Database name and path. E.g. c:\tmp\celldb.sqlite or /home/user/celldb.sql")

    parser.add_option("-p", dest="searchpath", 
                    metavar='search path', 
                    default=False,
                    help="Path were strs searches for res files To build the \
                    database.")
    (opt, args) = parser.parse_args()
################################################################################

if opt.db_input and opt.searchpath:
    print('\nIllegal combination of parameters. Create a database with --create-db\n')
    sys.exit()
    
d = vars(opt)  # command line options as dict

opts = False
for n in d:
    if d[n]:
        opts = True
    
if not opts:
    print('\n')
    parser.print_help()
    print('\n')
    sys.exit()

   
if opt.createdb and not opt.searchpath:
    print('\nPlease give a search path with the "-p" option to collect .res files.\n')
    sys.exit()
    
if not any([opt.createdb, opt.db_input]):
    print('\nA database file must be given (-c option) to either build or read a database.\n')
    sys.exit()

if opt.db_input:
    if not os.path.isfile(opt.db_input):
        print('\nParameter "-db ..." must be a file name.')
        sys.exit()
    if not opt.cell_abc:
        print('\nYou may need the "-s" parameter to sesrch in the database.\n')
        sys.exit()

def main(dbfilename = opt.createdb, inputdb = opt.db_input,
         searchpath=opt.searchpath, cell_abc=opt.cell_abc):
    print('\n')
        
    if inputdb:
        structures = StructureTable(inputdb)
        
    if dbfilename:
        if cell_abc and not os.path.isfile(dbfilename):
            print('Please create a database first!\n')
            sys.exit()
        if cell_abc and os.path.isfile(dbfilename):
            print('You may need parameter "-db" now.')
            sys.exit()
        if os.path.isfile(dbfilename):
            os.remove(dbfilename)
        structures = StructureTable(dbfilename)
        res = create_file_list(searchpath)
        if not res:
            print('could not find any .res files!')
            sys.exit()
        print('creating database')
        db = DatabaseRequest(dbfilename)
        db.initialize_db()
        print('filling file paths into database...')
        for i in res:
            structures.fill_structures_table(i[0], i[1])
        print('ready') 
        create_cells_table(structures)
    elif cell_abc:
        cell_search(structures, cell_abc)
#        big_cell_search(structures)
        

    
if __name__ == "__main__":
    reportlog = 'strs-bugreport.log'
    try:
        #cProfile.run('dsr = DSR(res_file_name="p21c.res")', 'foo.profile')
        if os.path.isfile(reportlog):
            os.remove(reportlog)
        main()
    except Exception:
        e = sys.exc_info()[1]
        import platform
        logging.basicConfig(filename=reportlog, filemode='w', level=logging.DEBUG)
        #os.remove(reportlog)
        logging.info('STRS version: {0}'.format(VERSION))
        logging.info('Python version: {0}'.format(sys.version))
        try:
            logging.info('Platform: {0} {1}, {2}'.format(platform.system(),
                               platform.release(), ' '.join(platform.uname())))
        except:
            pass
        logger = logging.getLogger('strs')
        ch = logging.StreamHandler()
        logger.addHandler(ch)
        print('\n\n')
        print('Congratulations! You found a bug in strs. Please send the file\n'\
              ' "strs-bugreport.log" to Daniel Kratzert, dkratzert@gmx.de\n')
        logger.exception(e)
    
    
    