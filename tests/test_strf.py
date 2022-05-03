"""
Unit tests for StructureFinder
"""
import os
import platform
import sys
import unittest
from contextlib import suppress
from pathlib import Path

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

import strf
from misc.version import VERSION
from searcher import database_handler

app = QApplication(sys.argv)


class TestApplication(unittest.TestCase):

    def setUp(self) -> None:
        # uic.compileUiDir('./gui')
        os.chdir(Path(__file__).parent.parent)
        app.setWindowIcon(QIcon('./icons/strf.png'))
        # Has to be without version number, because QWebengine stores data in ApplicationName directory:
        app.setApplicationName('StructureFinder')
        self.myapp = strf.StartStructureDB()
        self.myapp.setWindowTitle('StructureFinder v{}'.format(VERSION))
        os.chdir(Path(__file__).parent.parent)
        self.myapp.structures = database_handler.StructureTable('./test-data/test.sql')
        self.myapp.show_full_list()

    def tearDown(self) -> None:
        super(TestApplication, self).tearDown()
        app.closeAllWindows()

    # @unittest.skip("foo")
    def test_gui_simpl(self):
        # Number of items in main list
        self.assertEqual(263, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        # structureId
        self.assertEqual('241', self.myapp.ui.cifList_treeWidget.topLevelItem(1).text(3))
        # filename
        self.assertEqual('1000000.cif', self.myapp.ui.cifList_treeWidget.topLevelItem(1).text(0))

    # @unittest.skip('skipping unfinished')
    def test_search_cell_simpl(self):
        """
        Testing simple unit cell search.
        """
        # correct cell:
        self.myapp.ui.searchCellLineEDit.setText('7.878 10.469 16.068 90.000 95.147 90.000')
        self.assertEqual(3, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.myapp.show_full_list()
        # incomplete unit cell:
        self.myapp.ui.searchCellLineEDit.setText('7.878 10.469 16.068 90.000 95.147')
        self.assertEqual(263, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.myapp.show_full_list()
        # invalid unit cell:
        self.myapp.ui.searchCellLineEDit.setText('7.878 10.469 16.068 90.000 95.147 abc')
        self.assertEqual(263, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Not a valid unit cell!", self.myapp.statusBar().currentMessage())

    def test_search_text_simpl(self):
        """
        Testing simple text search.
        """
        self.myapp.ui.txtSearchEdit.setText('SADI')
        self.assertEqual(4, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 4 structures.", self.myapp.statusBar().currentMessage())
        self.assertEqual('breit_tb13_85.cif', self.myapp.ui.cifList_treeWidget.topLevelItem(0).text(0))
        self.assertEqual('p21c.cif', self.myapp.ui.cifList_treeWidget.topLevelItem(2).text(0))
        self.myapp.show_full_list()
        self.myapp.ui.txtSearchEdit.setText('sadi')
        self.assertEqual(4, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.myapp.show_full_list()
        # should give no result
        self.myapp.ui.txtSearchEdit.setText('foobar')
        self.assertEqual(0, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 0 structures.", self.myapp.statusBar().currentMessage())

    # @unittest.skip("foo")
    def test_clicks(self):
        """
        Testing copy to clip board with double click on unit cell
        """
        item = self.myapp.ui.cifList_treeWidget.topLevelItem(0)
        self.myapp.ui.cifList_treeWidget.setCurrentItem(item)
        QTest.mouseDClick(self.myapp.ui.cellField, Qt.LeftButton, delay=5)
        clp = QApplication.clipboard().text()
        self.assertEqual(" 7.878 10.469 16.068 90.000 95.147 90.000", clp)

    def test_save_db(self):
        """
        Saves the current database to a file.
        """
        self.myapp.import_file_dirs('test-data/COD')
        testfile = Path('./tst.sql')
        with suppress(Exception):
            Path.unlink(testfile)
        self.myapp.save_database(testfile.absolute())
        self.assertEqual(True, testfile.is_file())
        self.assertEqual(True, testfile.exists())
        Path.unlink(testfile)
        self.assertEqual(False, testfile.exists())
        self.assertEqual('Database saved.', self.myapp.statusBar().currentMessage())

    def test_index_db1(self):
        """
        Test index and save
        """
        self.myapp.import_file_dirs('test-data/COD')
        self.assertEqual(22, self.myapp.ui.cifList_treeWidget.topLevelItemCount())

    def test_index_db2(self):
        self.myapp.import_file_dirs('gui')
        self.assertEqual(0, self.myapp.ui.cifList_treeWidget.topLevelItemCount())

    def test_index_db3(self):
        self.myapp.import_file_dirs('test-data/tst')
        self.assertEqual(3, self.myapp.ui.cifList_treeWidget.topLevelItemCount())

    def test_index_db4(self):
        self.myapp.ui.add_cif.setChecked(False)
        self.myapp.ui.add_res.setChecked(True)
        self.myapp.import_file_dirs('test-data/tst')
        self.assertEqual(1, self.myapp.ui.cifList_treeWidget.topLevelItemCount())

    def test_open_database_file(self):
        """
        Testing the opening of a database.
        """
        # self.myapp.close_db()  # not needed here!
        status = self.myapp.open_database_file('test-data/test.sql')
        self.assertEqual(True, status)
        self.assertEqual(263, self.myapp.ui.cifList_treeWidget.topLevelItemCount())

    def test_p4p_parser(self):
        self.myapp.search_for_p4pcell('test-data/test2.p4p')
        self.assertEqual('14.637 9.221  15.094 90.000 107.186 90.000', self.myapp.ui.searchCellLineEDit.text())
        self.assertEqual(0, self.myapp.ui.cifList_treeWidget.topLevelItemCount())

    def test_res_parser(self):
        self.myapp.search_for_res_cell('test-data/p21c.res')
        self.assertEqual('10.509 20.904 20.507 90.000 94.130 90.000', self.myapp.ui.searchCellLineEDit.text())
        self.assertEqual(2, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 2 structures.", self.myapp.statusBar().currentMessage())

    def test_all_cif_values(self):
        item = self.myapp.ui.cifList_treeWidget.topLevelItem(3)
        self.myapp.ui.cifList_treeWidget.setCurrentItem(item)
        QTest.mouseClick(self.myapp.ui.allEntrysTab, Qt.LeftButton)
        self.assertEqual('Id', self.myapp.ui.allCifTreeWidget.topLevelItem(0).text(0))
        self.assertEqual('250', self.myapp.ui.allCifTreeWidget.topLevelItem(0).text(1))
        self.assertEqual('C107 H142 N14 O26', self.myapp.ui.allCifTreeWidget.topLevelItem(10).text(1))
        self.assertEqual(263, self.myapp.ui.cifList_treeWidget.topLevelItemCount())

    @unittest.skip(' ')
    def test_res_file_tab(self):
        item = self.myapp.ui.cifList_treeWidget.topLevelItem(261)
        self.myapp.ui.cifList_treeWidget.setCurrentItem(item)
        QTest.mouseClick(self.myapp.ui.SHELXtab, Qt.LeftButton)
        self.assertEqual('REM Solution', self.myapp.ui.SHELXplainTextEdit.toPlainText()[:12])

    def test_res_file3(self):
        item = self.myapp.ui.cifList_treeWidget.topLevelItem(250)
        self.myapp.ui.cifList_treeWidget.setCurrentItem(item)
        QTest.mouseClick(self.myapp.ui.SHELXtab, Qt.LeftButton)
        self.assertEqual('No SHELXL res file in cif found.', self.myapp.ui.SHELXplainTextEdit.toPlainText())

    def test_cellchekcsd(self):
        """
        Test if the unit cell of the current structure gets into the cellcheckcsd tab.
        """
        item = self.myapp.ui.cifList_treeWidget.topLevelItem(2)
        self.myapp.ui.cifList_treeWidget.setCurrentItem(item)
        QTest.mouseClick(self.myapp.ui.CCDCSearchTab, Qt.LeftButton)
        if platform.system() == 'Windows':
            self.assertEqual('7.8783  10.4689  16.068  90.0  95.147  90.0', self.myapp.ui.cellSearchCSDLineEdit.text())

    def test_adv_search_cell(self):
        """
        Tests for unit cells in advanced search mode.
        """
        # click on advanced search tab:
        os.chdir(Path(__file__).parent)
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        # fill in unit cell:
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check number of results:
        self.assertEqual(1, self.myapp.ui.cifList_tableView.model().rowCount())
        self.assertEqual("Found 1 structures.", self.myapp.statusBar().currentMessage())

        # back to adv search tab:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_unitCellLineEdit.clear()
        # fill in unit cell:
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        # avtivate more results checkbox:
        # QTest.mouseClick(self.myapp.ui.adv_moreResultscheckBox, Qt.LeftButton, delay=10)
        self.myapp.ui.adv_moreResultscheckBox.setChecked(True)
        self.myapp.ui.adv_superlatticeCheckBox.setChecked(False)
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check results
        self.assertEqual(2, self.myapp.ui.cifList_tableView.model().rowCount())
        self.assertEqual("Found 2 structures.", self.myapp.statusBar().currentMessage())

        # back to adv search tab:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_unitCellLineEdit.clear()
        # fill in unit cell:
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        # avtivate more results checkbox:
        # QTest.mouseClick(self.myapp.ui.adv_moreResultscheckBox, Qt.LeftButton, delay=10)
        self.myapp.ui.adv_moreResultscheckBox.setChecked(True)
        self.myapp.ui.adv_superlatticeCheckBox.setChecked(True)
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check results
        self.assertEqual(2, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 2 structures.", self.myapp.statusBar().currentMessage())

        # back to adv search tab:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_unitCellLineEdit.clear()
        # fill in unit cell:
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        # avtivate superlattice checkbox:
        self.myapp.ui.adv_moreResultscheckBox.setChecked(False)
        self.myapp.ui.adv_superlatticeCheckBox.setChecked(True)
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check results
        self.assertEqual(1, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 1 structures.", self.myapp.statusBar().currentMessage())

    def test_adv_search_text(self):
        """
        Searching for text advanced.
        """
        # self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        # click on advanced search tab:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_textsearch.setText('SADI')
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(4, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 4 structures.", self.myapp.statusBar().currentMessage())
        self.assertEqual('breit_tb13_85.cif', self.myapp.ui.cifList_treeWidget.topLevelItem(0).text(0))
        self.assertEqual('p21c.cif', self.myapp.ui.cifList_treeWidget.topLevelItem(2).text(0))
        self.assertEqual(True, self.myapp.ui.MaintabWidget.isVisible())

        # now exclude some:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_textsearch.setText('SADI')
        self.myapp.ui.adv_textsearch_excl.setText('breit')
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(2, self.myapp.ui.cifList_treeWidget.topLevelItemCount())

        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_textsearch.setText('SADI')
        self.myapp.ui.adv_textsearch_excl.setText('breit')
        # additionally include only spgrp 14:
        self.myapp.ui.SpGrpComboBox.setCurrentIndex(14)
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(1, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 1 structures.", self.myapp.statusBar().currentMessage())

        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_textsearch_excl.clear()
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N')
        # additionally include only spgrp 14:
        self.myapp.ui.SpGrpComboBox.setCurrentIndex(5)
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(2, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 2 structures.", self.myapp.statusBar().currentMessage())

    # @unittest.skip
    def test_txt_elex_elin(self):
        self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.assertEqual(True, self.myapp.ui.adv_searchtab.isVisible())
        self.assertEqual(False, self.myapp.ui.cifList_treeWidget.isVisible())
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N')
        self.myapp.ui.SpGrpComboBox.setCurrentIndex(5)
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(2, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 2 structures.", self.myapp.statusBar().currentMessage())

    def test_zero_results_elexcl(self):
        # self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N F')
        self.myapp.advanced_search()
        # In this case (zero results), the cifList_treeWidget will not be updated!!!
        self.assertEqual(263, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 0 structures.", self.myapp.statusBar().currentMessage())

    def test_one_result_date1(self):
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N')
        self.myapp.ui.dateEdit1.setDate(QDate(2017, 7, 22))  # two days after the older structure was edited
        self.myapp.advanced_search()
        # In this case (zero results), the cifList_treeWidget will not be updated!!!
        self.assertEqual(1, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 1 structures.", self.myapp.statusBar().currentMessage())

    def test_zero_result_date1_sadi_excl(self):
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_textsearch_excl.setText('sadi')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N')
        self.myapp.ui.dateEdit1.setDate(QDate(2017, 7, 22))  # two days after the older structure was edited
        self.myapp.advanced_search()
        # In this case (zero results), the cifList_treeWidget will not be updated!!!
        self.assertEqual(263, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 0 structures.", self.myapp.statusBar().currentMessage())
        self.myapp.ui.adv_textsearch_excl.setText('foobar')
        self.myapp.advanced_search()
        self.assertEqual(1, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 1 structures.", self.myapp.statusBar().currentMessage())

    def test_superlatice_exclelements(self):
        # back to adv search tab:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        # fill in unit cell:
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        self.myapp.ui.adv_elementsExclLineEdit.setText('Cl')
        # avtivate more results checkbox:
        self.assertEqual(True, self.myapp.ui.adv_moreResultscheckBox.isVisible())
        self.assertEqual(False, self.myapp.ui.adv_moreResultscheckBox.isChecked())
        self.myapp.ui.adv_moreResultscheckBox.setChecked(True)
        self.myapp.ui.adv_superlatticeCheckBox.setChecked(True)
        self.assertEqual(True, self.myapp.ui.adv_moreResultscheckBox.isChecked())
        self.assertEqual(True, self.myapp.ui.adv_superlatticeCheckBox.isChecked())
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check results
        self.assertEqual(1, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 1 structures.", self.myapp.statusBar().currentMessage())

    def test_superlatice_onlythese(self):
        # back to adv search tab:
        self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        # fill in unit cell:
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H Cl N O')
        self.myapp.ui.onlyTheseElementsCheckBox.setChecked(True)
        # avtivate more results checkbox:
        self.assertEqual(True, self.myapp.ui.adv_moreResultscheckBox.isVisible())
        self.assertEqual(False, self.myapp.ui.adv_moreResultscheckBox.isChecked())
        self.myapp.ui.adv_moreResultscheckBox.setChecked(True)
        self.myapp.ui.adv_superlatticeCheckBox.setChecked(True)
        self.assertEqual(True, self.myapp.ui.adv_moreResultscheckBox.isChecked())
        self.assertEqual(True, self.myapp.ui.adv_superlatticeCheckBox.isChecked())
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check results
        self.assertEqual(1, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 1 structures.", self.myapp.statusBar().currentMessage())

    def test_r1_val_find(self):
        self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        self.myapp.ui.adv_R1_search_line.setText('2.5')
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(2, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 2 structures.", self.myapp.statusBar().currentMessage())

    def test_r1_val_nofind(self):
        self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        self.myapp.ui.adv_R1_search_line.setText('0')
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # returns full list:
        self.assertEqual(263, self.myapp.ui.cifList_treeWidget.topLevelItemCount())
        self.assertEqual("Found 0 structures.", self.myapp.statusBar().currentMessage())

