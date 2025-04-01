"""
Unit tests for StructureFinder
"""
import platform
import unittest
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Union

from PyQt5.QtCore import QDate, QEventLoop, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from structurefinder import strf
from structurefinder.misc.version import VERSION
from structurefinder.searcher import database_handler
from structurefinder.searcher.misc import COL_FILE, COL_ID

"""
These tests only run with pytest, because they rely on the PYTEST_CURRENT_TEST environment variable.
"""


class TestApplication(unittest.TestCase):

    def setUp(self) -> None:
        database_handler.columns.reset_defaults()
        strf.app.setWindowIcon(QIcon('./icons/strf.png'))
        # Has to be without version number, because QWebengine stores data in ApplicationName directory:
        strf.app.setApplicationName('StructureFinder')
        self.myapp = strf.StartStructureDB(db_file_name='./tests/test-data/test.sql')
        self.myapp.setWindowTitle(f'StructureFinder v{VERSION}')
        self.myapp.ui.hideInArchivesCB.setChecked(False)
        self.myapp.settings.save_visible_headers([])

    def tearDown(self) -> None:
        self.myapp.close()

    def get_row_content(self, row: int, col: int) -> Union[str, int]:
        model = self.myapp.table_model
        source_index = model.index(row, col)
        row_content = model.data(source_index)
        return row_content

    def get_row_count_from_table(self):
        return self.myapp.ui.cifList_tableView.model().rowCount()

    def wait_for_worker(self):
        counter = 0
        sleep(0.1)
        while not self.get_row_count_from_table():
            strf.app.processEvents(QEventLoop.AllEvents, 200)
            if counter > 10:
                break
            counter += 1
            sleep(0.1)
        sleep(0.1)

    def test_gui_simpl(self):
        # Number of items in main list
        self.assertEqual(263, self.get_row_count_from_table())
        # structureId
        self.assertEqual(2, self.get_row_content(1, COL_ID))
        # filename
        self.assertEqual('2004924.cif', self.get_row_content(1, COL_FILE))

    def test_search_cell_simpl(self):
        """
        Testing simple unit cell search.
        """
        # Table rows before search:
        self.assertEqual(263, self.get_row_count_from_table())
        # correct cell:
        self.myapp.ui.searchCellLineEDit.setText('7.878 10.469 16.068 90.000 95.147 90.000')
        self.assertEqual(3, self.get_row_count_from_table())

    def test_show_full_list(self):
        self.myapp.show_full_list()
        self.assertEqual(263, self.get_row_count_from_table())

    def test_search_incomplete_cell(self):
        # incomplete unit cell:
        self.myapp.ui.searchCellLineEDit.setText('7.878 10.469 16.068 90.000 95.147')
        # still full list:
        self.assertEqual(263, self.get_row_count_from_table())

    def test_invalid_cell(self):
        # invalid unit cell:
        self.myapp.ui.searchCellLineEDit.setText('7.878 10.469 16.068 90.000 95.147 abc')
        self.assertEqual(263, self.get_row_count_from_table())
        self.assertEqual("Not a valid unit cell!", self.myapp.statusBar().currentMessage())

    def test_search_text_simpl(self):
        """
        Testing simple text search.
        """
        self.myapp.ui.txtSearchEdit.setText('SADI')
        self.assertEqual(4, self.get_row_count_from_table())

    def test_search_text_simpl_lower(self):
        self.myapp.ui.txtSearchEdit.setText('sadi')
        self.assertEqual(4, self.get_row_count_from_table())

    def test_statusbar_message(self):
        self.myapp.ui.txtSearchEdit.setText('sadi')
        self.assertEqual("Found 4 structures.", self.myapp.statusBar().currentMessage())

    def test_data_name_column(self):
        self.myapp.ui.txtSearchEdit.setText('sadi')
        self.assertEqual('p21c.res', self.get_row_content(1, COL_FILE))

    def test_no_result(self):
        self.myapp.ui.txtSearchEdit.setText('foobar')
        self.assertEqual(0, self.get_row_count_from_table())
        self.assertEqual("Found 0 structures.", self.myapp.statusBar().currentMessage())

    def test_clicks(self):
        """
        Testing copy to clip board with double click on unit cell
        """
        self.myapp.ui.cifList_tableView.selectRow(0)
        QTest.mouseDClick(self.myapp.ui.cellField, Qt.LeftButton, delay=5)
        clp = QApplication.clipboard().text()
        self.assertEqual("10.360 18.037 25.764 127.030 129.810 90.510", clp)

    # @pytest.mark.skip(reason="Not working an all systems'")
    def test_save_db(self):
        """
        Saves the current database to a file.
        """
        testfile = Path('./tst.sql')
        with suppress(Exception):
            Path.unlink(testfile)
        self.myapp.import_file_dirs('test-data/COD')
        self.wait_for_worker()
        self.myapp.save_database(testfile.resolve())
        self.assertEqual(True, testfile.is_file())
        self.assertEqual(True, testfile.exists())
        Path.unlink(testfile)
        self.assertEqual(False, testfile.exists())
        self.assertEqual('Database saved.', self.myapp.statusBar().currentMessage())

    # @pytest.mark.skip(reason="Not working an all systems'")
    def test_index_db1(self):
        """
        Test index and save
        """
        self.myapp.import_file_dirs('tests/test-data/COD')
        self.wait_for_worker()
        self.myapp.show_full_list()
        self.assertEqual(22, self.get_row_count_from_table())

    # @pytest.mark.skip(reason="Not working an all systems'")
    def test_index_db2(self):
        self.myapp.import_file_dirs('gui')
        self.wait_for_worker()
        self.assertEqual(0, self.get_row_count_from_table())

    # @pytest.mark.skip(reason="Not working an all systems'")
    def test_index_db3(self):
        self.myapp.import_file_dirs('tests/test-data/tst')
        self.wait_for_worker()
        self.assertEqual(3, self.get_row_count_from_table())

    # @pytest.mark.skip(reason="Not working an all systems'")
    def test_index_db_only_res_files(self):
        self.myapp.ui.add_cif.setChecked(False)
        self.myapp.ui.add_res.setChecked(True)
        self.myapp.import_file_dirs('tests/test-data/tst')
        self.wait_for_worker()
        self.assertEqual(1, self.get_row_count_from_table())

    # @pytest.mark.skip(reason="Not working an all systems'")
    def test_index_db_only_cif_files(self):
        self.myapp.ui.add_cif.setChecked(True)
        self.myapp.ui.add_res.setChecked(False)
        self.myapp.import_file_dirs('tests/test-data/tst')
        self.wait_for_worker()
        self.assertEqual(2, self.get_row_count_from_table())

    def test_open_database_file(self):
        """
        Testing the opening of a database.
        """
        status = self.myapp.open_database_file('tests/test-data/test.sql')
        self.assertEqual(True, status)
        self.assertEqual(263, self.get_row_count_from_table())

    def test_filter_archives(self):
        self.myapp.ui.hideInArchivesCB.setChecked(False)
        status = self.myapp.open_database_file('tests/test-data/test.sql')
        self.assertEqual(263, self.get_row_count_from_table())
        self.myapp.ui.hideInArchivesCB.setChecked(True)
        # Rows without archives:
        self.assertEqual(51, self.get_row_count_from_table())

    def test_p4p_parser(self):
        self.myapp.search_for_p4pcell('tests/test-data/test2.p4p')
        self.assertEqual('14.637 9.221  15.094 90.000 107.186 90.000', self.myapp.ui.searchCellLineEDit.text())

    def test_res_parser(self):
        self.myapp.search_for_res_cell('tests/test-data/p21c.res')
        self.assertEqual('10.509 20.904 20.507 90.000 94.130 90.000', self.myapp.ui.searchCellLineEDit.text())

    def test_all_cif_values(self):
        self.myapp.ui.cifList_tableView.selectRow(249)
        QTest.mouseClick(self.myapp.ui.allEntrysTab, Qt.LeftButton)
        self.assertEqual('Id', self.myapp.ui.allCifTreeWidget.topLevelItem(0).text(0))
        self.assertEqual('250', self.myapp.ui.allCifTreeWidget.topLevelItem(0).text(1))
        self.assertEqual('C107 H142 N14 O26', self.myapp.ui.allCifTreeWidget.topLevelItem(10).text(1))
        self.assertEqual(263, self.get_row_count_from_table())

    def test_res_file_tab(self):
        self.myapp.ui.cifList_tableView.selectRow(2)
        QTest.mouseClick(self.myapp.ui.SHELXtab, Qt.LeftButton)
        self.assertEqual('REM Solution', self.myapp.ui.SHELXplainTextEdit.toPlainText()[:12])

    def test_res_file3(self):
        self.myapp.ui.cifList_tableView.selectRow(250)
        QTest.mouseClick(self.myapp.ui.SHELXtab, Qt.LeftButton)
        self.assertEqual('No SHELXL res file in cif found.', self.myapp.ui.SHELXplainTextEdit.toPlainText())

    @unittest.skip('Can not run this on Github')
    def test_cellchekcsd(self):
        """
        Test if the unit cell of the current structure gets into the cellcheckcsd tab.
        """
        self.myapp.ui.cifList_tableView.selectRow(2)
        QTest.mouseClick(self.myapp.ui.CCDCSearchTab, Qt.LeftButton)
        if platform.system() == 'Windows':
            self.assertEqual('23.6015  20.9757  26.1674  90.0  101.784  90.0',
                             self.myapp.ui.cellSearchCSDLineEdit.text())

    # @unittest.skip('Can not run this on Github')
    def test_advanced_mode_search_cell(self):
        """
        Tests for unit cells in advanced search mode.
        """
        # click on advanced search tab:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        # fill in unit cell:
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check number of results:
        self.assertEqual(1, self.get_row_count_from_table())
        self.assertEqual("Found 1 structures.", self.myapp.statusBar().currentMessage())

    def test_advanced_with_more_results(self):
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        # fill in unit cell:
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        # avtivate more results checkbox:
        QTest.mouseClick(self.myapp.ui.adv_moreResultscheckBox, Qt.LeftButton, delay=10)
        self.myapp.ui.adv_moreResultscheckBox.setChecked(True)
        self.myapp.ui.adv_superlatticeCheckBox.setChecked(False)
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check results
        self.assertEqual(1, self.get_row_count_from_table())

    def test_advanced_with_more_results_and_superlattice(self):
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        # avtivate more results checkbox:
        # QTest.mouseClick(self.myapp.ui.adv_moreResultscheckBox, Qt.LeftButton, delay=10)
        self.myapp.ui.adv_moreResultscheckBox.setChecked(True)
        self.myapp.ui.adv_superlatticeCheckBox.setChecked(True)
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check results
        self.assertEqual(1, self.get_row_count_from_table())

    def test_advanced_with_superlattice_only(self):
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        # avtivate superlattice checkbox:
        self.myapp.ui.adv_moreResultscheckBox.setChecked(False)
        self.myapp.ui.adv_superlatticeCheckBox.setChecked(True)
        # click on search button:
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # check results
        self.assertEqual(1, self.get_row_count_from_table())

    def test_adv_search_text(self):
        """
        Searching for text advanced.
        """
        # click on advanced search tab:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_textsearch.setText('SADI')
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(4, self.get_row_count_from_table())
        self.assertEqual('breit_tb13_85.cif', self.get_row_content(0, 2))
        self.assertEqual('p21c.cif', self.get_row_content(3, 2))
        self.assertEqual('2018-09-05', self.get_row_content(3, 3))
        self.assertEqual(True, self.myapp.ui.MaintabWidget.isVisible())

    def test_search_text_with_exclude(self):
        # now exclude some:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_textsearch.setText('SADI')
        self.myapp.ui.adv_textsearch_excl.setText('breit')
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(2, self.get_row_count_from_table())

    def test_search_text_with_exclude_and_include_spgr(self):
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_textsearch.setText('SADI')
        self.myapp.ui.adv_textsearch_excl.setText('breit')
        # additionally include only spgrp 14:
        self.myapp.ui.SpGrpComboBox.setCurrentIndex(14)
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(1, self.get_row_count_from_table())

    def test_search_text_and_elements(self):
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.adv_textsearch_excl.clear()
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N')
        # additionally include only spgrp 14:
        self.myapp.ui.SpGrpComboBox.setCurrentIndex(5)
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(2, self.get_row_count_from_table())

    # @unittest.skip
    def test_txt_elex_elin(self):
        self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.assertEqual(True, self.myapp.ui.adv_searchtab.isVisible())
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N')
        self.myapp.ui.SpGrpComboBox.setCurrentIndex(5)
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(2, self.get_row_count_from_table())

    def test_zero_results_elexcl(self):
        # self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N F')
        self.myapp.advanced_search()
        # In this case (zero results), the cifList_tableView will show all entries!!!
        self.assertEqual(263, self.get_row_count_from_table())
        self.assertEqual("Found 0 structures.", self.myapp.statusBar().currentMessage())

    def test_one_result_date1(self):
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N')
        self.myapp.ui.dateEdit1.setDate(QDate(2017, 7, 22))  # two days after the older structure was edited
        self.myapp.advanced_search()
        # In this case (zero results), the cifList_treeWidget will not be updated!!!
        self.assertEqual(1, self.get_row_count_from_table())

    def test_zero_result_date1_sadi_excl(self):
        self.myapp.ui.adv_textsearch.setText('Breit')
        self.myapp.ui.adv_textsearch_excl.setText('sadi')
        self.myapp.ui.adv_elementsIncLineEdit.setText('C H O')
        self.myapp.ui.adv_elementsExclLineEdit.setText('N')
        self.myapp.ui.dateEdit1.setDate(QDate(2017, 7, 22))  # two days after the older structure was edited
        self.myapp.advanced_search()
        # In this case (zero results), the cifList_treeWidget will not be updated!!!
        self.assertEqual(263, self.get_row_count_from_table())
        self.assertEqual("Found 0 structures.", self.myapp.statusBar().currentMessage())
        self.myapp.ui.adv_textsearch_excl.setText('foobar')
        self.myapp.advanced_search()
        self.assertEqual(1, self.get_row_count_from_table())
        self.assertEqual("Found 1 structures.", self.myapp.statusBar().currentMessage())

    def test_superlatice_exclelements(self):
        # back to adv search tab:
        QTest.mouseClick(self.myapp.ui.adv_searchtab, Qt.LeftButton)
        self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        # fill in unit cell:
        self.myapp.ui.adv_unitCellLineEdit.setText('10.930 12.716 15.709 90.000 90.000 90.000')
        # self.myapp.ui.adv_elementsExclLineEdit.setText('Cl')
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
        self.assertEqual(1, self.myapp.ui.cifList_tableView.model().rowCount())

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
        self.assertEqual(1, self.get_row_count_from_table())

    def test_r1_val_find(self):
        self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        self.myapp.ui.adv_R1_search_line.setText('2.5')
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        self.assertEqual(2, self.get_row_count_from_table())

    def test_r1_val_nofind(self):
        self.myapp.ui.MaintabWidget.setCurrentIndex(3)
        self.myapp.ui.adv_R1_search_line.setText('0')
        QTest.mouseClick(self.myapp.ui.adv_SearchPushButton, Qt.LeftButton)
        # returns full list:
        self.assertEqual(263, self.get_row_count_from_table())
