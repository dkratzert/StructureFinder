"""
Unit tests for StructureFinder
"""
import doctest
import unittest

import searcher
import shelxfile
import strf
from lattice import lattice
from misc import update_check
from searcher import database_handler


class doctestsTest(unittest.TestCase):
    def testrun_doctest(self):
        for name in [strf, shelxfile, searcher, update_check]:
            failed, attempted = doctest.testmod(name)  # , verbose=True)
            if failed == 0:
                print('passed all {} tests in {}!'.format(attempted, name.__name__))
            else:
                msg = '!!!!!!!!!!!!!!!! {} of {} tests failed in {}  !!!!!!!!!!!!!!!!!!!!!!!!!!!'.format(failed,
                                                                                                         attempted,
                                                                                                         name.__name__)
                self.assertFalse(failed, msg)


class TestSearch(unittest.TestCase):
    def setUp(self) -> None:
        self.dbfilename = 'test.sql'
        self.structures = database_handler.StructureTable(self.dbfilename)


    def test_cellfind(self):
        cell = []
        volume = lattice.vol_unitcell(*cell)
        self.structures.find_by_volume()
