"""
Unit tests for StructureFinder
"""
import doctest
import sys
import unittest

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

import searcher
import searcher.misc
import strf
from misc import update_check
from misc.version import VERSION
from pymatgen.core import lattice
from searcher import database_handler, fileparser
from shelxfile import shelx, elements, misc


class DoctestsTest(unittest.TestCase):
    def testrun_doctest(self):
        for name in [strf, shelx, elements, misc, searcher, update_check, database_handler, fileparser]:
            failed, attempted = doctest.testmod(name)  # , verbose=True)
            if failed == 0:
                print('passed all {} tests in {}!'.format(attempted, name.__name__))
            else:
                msg = '!!!!!!!!!!!!!!!! {} of {} tests failed in {}  !!!!!!!!!!!!!!!!!!!!!!!!!!!'.format(failed,
                                                                                                         attempted,
                                                                                                         name.__name__)
                self.assertFalse(failed, msg)


class TestApplication(unittest.TestCase):

    def setUp(self) -> None:
        #uic.compileUiDir('./gui')
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon('./icons/strf.png'))
        # Has to be without version number, because QWebengine stores data in ApplicationName directory:
        self.app.setApplicationName('StructureFinder')
        self.myapp = strf.StartStructureDB()
        self.myapp.setWindowTitle('StructureFinder v{}'.format(VERSION))
        self.myapp.structures = database_handler.StructureTable('./test-data/test.sql')
        self.myapp.show_full_list()

    def tearDown(self) -> None:
        super(TestApplication, self).tearDown()

    #@unittest.skip("foo")
    def test_search_cell_simpl(self):
        # Number of items in main list
        self.assertEqual(263, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        # structureId
        self.assertEqual('241', self.myapp.ui.cifList_treeWidget.topLevelItem(1).text(3))
        # filename
        self.assertEqual('1000000.cif', self.myapp.ui.cifList_treeWidget.topLevelItem(1).text(0))

    # @unittest.skip('skipping unfinished')
    def test_search_text_simpl(self):
        """
        Testing simple unit cell search.
        """
        self.myapp.ui.searchCellLineEDit.setText('7.878 10.469 16.068 90.000 95.147 90.000')
        #QTest.qSleep(100)
        self.assertEqual(3, self.myapp.ui.cifList_treeWidget.topLevelItemCount())

    @unittest.skip("foo")
    def test_clicks(self):
        """
        Testing copy to clip board with double click on unit cell
        """
        item = self.myapp.ui.cifList_treeWidget.topLevelItem(0)
        self.myapp.ui.cifList_treeWidget.setCurrentItem(item)
        QTest.mouseDClick(self.myapp.ui.cellField, Qt.LeftButton, delay=5)
        clp = QApplication.clipboard().text()
        self.assertEqual(" 7.878 10.469 16.068 90.000 95.147 90.000", clp)


class TestSearch(unittest.TestCase):
    def setUp(self) -> None:
        self.dbfilename = 'test-data/test.sql'
        self.structures = database_handler.StructureTable(self.dbfilename)
        # more results:
        self.m_vol_threshold = 0.04
        self.m_ltol = 0.08
        self.m_atol = 1.8
        # regular:
        self.vol_threshold = 0.02
        self.ltol = 0.03
        self.atol = 1.0

    def test_cellfind(self):
        idlist = []
        cell = [10.930, 12.716, 15.709, 90.000, 90.000, 90.000]
        results = [(49, 9.242, 12.304, 18.954, 90.0, 92.74, 90.0, 2153.0),
                   (260, 10.93, 12.7162, 15.7085, 90.0, 90.0, 90.0, 2183.3),
                   (10, 13.5918, 10.7345, 16.442, 90.0, 113.142, 90.0, 2205.9),
                   (244, 13.5918, 10.7345, 16.442, 90.0, 113.142, 90.0, 2205.9),
                   (207, 16.139, 5.117, 26.887, 90.0, 90.0, 90.0, 2220.4)]
        volume = searcher.misc.vol_unitcell(*cell)
        cells = self.structures.find_by_volume(volume, self.vol_threshold)
        self.assertEqual(cells, results)
        lattice1 = lattice.Lattice.from_parameters_niggli_reduced(*cell)
        for curr_cell in cells:
            try:
                lattice2 = lattice.Lattice.from_parameters(*curr_cell[1:7])
            except ValueError:
                continue
            mapping = lattice1.find_mapping(lattice2, self.ltol, self.atol, skip_rotation_matrix=True)
            if mapping:
                idlist.append(curr_cell[0])
        self.assertEqual(idlist, [260])

    def test_more_results_cellfind(self):
        idlist = []
        cell = [10.930, 12.716, 15.709, 90.000, 90.000, 90.000]
        results = [(251, 13.432, 10.5988, 16.2393, 90.0, 113.411, 90.0, 2121.6),
                   (161, 14.8208, 8.1939, 17.4844, 90.0, 91.185, 90.0, 2122.9),
                   (49, 9.242, 12.304, 18.954, 90.0, 92.74, 90.0, 2153.0),
                   (260, 10.93, 12.7162, 15.7085, 90.0, 90.0, 90.0, 2183.3),
                   (10, 13.5918, 10.7345, 16.442, 90.0, 113.142, 90.0, 2205.9),
                   (244, 13.5918, 10.7345, 16.442, 90.0, 113.142, 90.0, 2205.9),
                   (207, 16.139, 5.117, 26.887, 90.0, 90.0, 90.0, 2220.4),
                   (71, 14.815, 14.264, 10.55, 90.0, 90.0, 90.0, 2229.4),
                   (113, 15.187, 12.883, 11.468, 90.0, 90.0, 90.0, 2243.8),
                   (129, 27.858, 8.094, 9.951, 90.0, 90.0, 90.0, 2243.8),
                   (1, 10.36, 18.037, 25.764, 127.03, 129.81, 90.51, 2260.487670154818),
                   (12, 10.36, 18.037, 25.764, 127.03, 129.81, 90.51, 2260.487670154818)]
        volume = searcher.misc.vol_unitcell(*cell)
        cells = self.structures.find_by_volume(volume, self.m_vol_threshold)
        self.assertEqual(cells, results)
        lattice1 = lattice.Lattice.from_parameters_niggli_reduced(*cell)
        for curr_cell in cells:
            try:
                lattice2 = lattice.Lattice.from_parameters(*curr_cell[1:7])
            except ValueError:
                continue
            mapping = lattice1.find_mapping(lattice2, self.m_ltol, self.m_atol, skip_rotation_matrix=True)
            if mapping:
                idlist.append(curr_cell[0])
        self.assertEqual(idlist, [260, 113])
