#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <daniel.kratzert@uni-freiburg.de> wrote this file. As long as you retain this
* notice you can do whatever you want with this stuff. If we meet some day, and
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: Daniel Kratzert
"""
import math
import os
import shutil
import sys
import tempfile
import time
from datetime import date
from os.path import isfile, samefile
from pathlib import Path
from sqlite3 import DatabaseError, ProgrammingError, OperationalError
from displaymol.sdm import SDM

from PyQt5.QtCore import QModelIndex, pyqtSlot, QUrl, QDate, QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QProgressBar, QPushButton, QTreeWidgetItem, QMainWindow

from p4pfile.p4p_reader import P4PFile, read_file_to_list
from shelxfile.misc import chunks
from shelxfile.shelx import ShelXFile

DEBUG = False

from apex import apeximporter
from displaymol import mol_file_writer, write_html
from lattice import lattice
from misc.version import VERSION
from pymatgen.core import mat_lattice
from searcher import constants, misc, filecrawler, database_handler
from searcher.constants import centering_num_2_letter, centering_letter_2_num
from searcher.fileparser import Cif
from searcher.misc import is_valid_cell, elements, flatten, combine_results

is_windows = False
import platform
if platform.system() == 'Windows':
    is_windows = True

try:
    from xml.etree.ElementTree import ParseError
    from ccdc.query import get_cccsd_path, search_csd, parse_results
except ModuleNotFoundError:
    pass

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except Exception as e:
    print(e, '# Unable to import QWebEngineView')
    if DEBUG:
        raise

"""
TODO:
- sort results by G6 distance
- Use QPainter to draw molecule?

Search for:
- draw structure (with JSME? Acros? Kekule?, https://github.com/ggasoftware/ketcher)
- compare  molecules https://groups.google.com/forum/#!msg/networkx-discuss/gC_-Wc0bRWw/ISRZYFsPCQAJ
  - search algorithms
  http://chemmine.ucr.edu/help/#similarity, https://en.wikipedia.org/wiki/Jaccard_index
"""
# This is to make sure that strf finds the application path even when it is
# executed from another path e.g. when opened via "open file" in windows:
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


class StartStructureDB(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        self.statusBar().showMessage('StructureFinder version {}'.format(VERSION))
        self.ui.cifList_treeWidget.show()
        self.ui.cifList_treeWidget.hideColumn(3)
        self.dbfdesc = None
        self.dbfilename = None
        self.tmpfile = False  # indicates wether a tmpfile or any other db file is used
        # self.ui.centralwidget.setMinimumSize(1000, 500)
        self.abort_import_button = QPushButton("Abort")
        self.progress = QProgressBar(self)
        self.progress.setFormat('')
        self.ui.statusbar.addWidget(self.progress)
        self.ui.statusbar.addWidget(self.abort_import_button)
        self.structures = None
        self.apx = None
        self.structureId = '0'
        self.passwd = ''
        if is_windows:  # Not valid for MacOS
            # Check for CellCheckCSD:
            if not get_cccsd_path():
                self.ui.cellSearchCSDLineEdit.setText('You need to install CellCheckCSD in order to search here.')
                self.ui.cellSearchCSDLineEdit.setDisabled(True)
                self.ui.CSDpushButton.setDisabled(True)
        else:
            self.ui.cellSearchCSDLineEdit.setText('You need to install CellCheckCSD in order to search here.')
            self.ui.cellSearchCSDLineEdit.setDisabled(True)
            self.ui.CSDpushButton.setDisabled(True)
        self.show()
        self.setAcceptDrops(True)
        self.full_list = True  # indicator if the full structures list is shown
        self.decide_import = True
        self.connect_signals_and_slots()
        # Set both to today() to distinquish between a modified and unmodified date field.
        self.ui.dateEdit1.setDate(QDate(date.today()))
        self.ui.dateEdit2.setDate(QDate(date.today()))
        try:
            self.write_empty_molfile(mol_data=' ')
        except Exception as e:
            # Graphics driver not compatible
            print(e, '##')
            #raise
        try:
            self.init_webview()
        except Exception as e:
            print(e, '###')
            #raise
        self.ui.MaintabWidget.setCurrentIndex(0)
        self.setWindowIcon(QIcon(os.path.join(application_path, './icons/strf.png')))
        self.uipass = Ui_PasswdDialog()
        # self.ui.cifList_treeWidget.sortByColumn(0, 0)
        # Actions for certain gui elements:
        self.ui.cellField.addAction(self.ui.actionCopy_Unit_Cell)
        self.ui.cifList_treeWidget.addAction(self.ui.actionGo_to_All_CIF_Tab)
        if len(sys.argv) > 1:
            self.dbfilename = sys.argv[1]
            if isfile(self.dbfilename):
                try:
                    self.structures = database_handler.StructureTable(self.dbfilename)
                    self.show_full_list()
                except (IndexError, DatabaseError) as e:
                    print(e)
                    if DEBUG:
                        raise
        # select the first item in the list
        item = self.ui.cifList_treeWidget.topLevelItem(0)
        self.ui.cifList_treeWidget.setCurrentItem(item)
        self.ui.SumformLabel.setMinimumWidth(self.ui.reflTotalLineEdit.width())


    def connect_signals_and_slots(self):
        """
        Connects the signals and slot.
        The actionExit signal is connected in the ui file.
        """
        # Buttons:
        self.ui.importDatabaseButton.clicked.connect(self.import_cif_database)
        self.ui.saveDatabaseButton.clicked.connect(self.save_database)
        self.ui.importDirButton.clicked.connect(self.import_cif_dirs)
        self.ui.openApexDBButton.clicked.connect(self.import_apex_db)
        self.ui.closeDatabaseButton.clicked.connect(self.close_db)
        self.abort_import_button.clicked.connect(self.abort_import)
        self.ui.moreResultsCheckBox.stateChanged.connect(self.cell_state_changed)
        self.ui.sublattCheckbox.stateChanged.connect(self.cell_state_changed)
        self.ui.ad_SearchPushButton.clicked.connect(self.advanced_search)
        self.ui.ad_ClearSearchButton.clicked.connect(self.show_full_list)
        if is_windows:
            self.ui.CSDpushButton.clicked.connect(self.search_csd_and_display_results)
        # Actions:
        self.ui.actionClose_Database.triggered.connect(self.close_db)
        self.ui.actionImport_directory.triggered.connect(self.import_cif_dirs)
        self.ui.actionImport_file.triggered.connect(self.import_cif_database)
        self.ui.actionSave_Database.triggered.connect(self.save_database)
        self.ui.actionCopy_Unit_Cell.triggered.connect(self.copyUnitCell)
        self.ui.actionGo_to_All_CIF_Tab.triggered.connect(self.on_click_item)
        # Other fields:
        self.ui.txtSearchEdit.textChanged.connect(self.search_text)
        self.ui.searchCellLineEDit.textChanged.connect(self.search_cell)
        self.ui.p4pCellButton.clicked.connect(self.get_name_from_p4p)
        self.ui.cifList_treeWidget.itemDoubleClicked.connect(self.on_click_item)
        self.ui.CSDtreeWidget.itemDoubleClicked.connect(self.show_csdentry)
        self.ui.ad_elementsIncLineEdit.textChanged.connect(self.elements_fields_check)
        self.ui.ad_elementsExclLineEdit.textChanged.connect(self.elements_fields_check)
        self.ui.add_res.clicked.connect(self.res_checkbox_clicked)
        self.ui.add_cif.clicked.connect(self.cif_checkbox_clicked)
        self.ui.cifList_treeWidget.selectionModel().currentChanged.connect(self.get_properties)
        self.ui.growCheckBox.toggled.connect(self.redraw_molecule)

    def res_checkbox_clicked(self, click):
        if not any([self.ui.add_res.isChecked(), self.ui.add_cif.isChecked()]):
            self.ui.add_cif.setChecked(True)

    def cif_checkbox_clicked(self, click):
        if not any([self.ui.add_res.isChecked(), self.ui.add_cif.isChecked()]):
            self.ui.add_cif.setChecked(True)

    def on_click_item(self, item):
        self.ui.MaintabWidget.setCurrentIndex(1)

    def show_csdentry(self, item: QModelIndex):
        import webbrowser
        sel = self.ui.CSDtreeWidget.selectionModel().selection()
        try:
            identifier = sel.indexes()[8].data()
        except KeyError:
            return None
        webbrowser.open_new_tab('https://www.ccdc.cam.ac.uk/structures/Search?entry_list=' + identifier)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        Handles drop events.
        """
        from urllib.parse import urlparse
        p = urlparse(e.mimeData().text())
        if sys.platform.startswith('win'):
            final_path = p.path[1:]  # remove strange / at start
        else:
            final_path = p.path
        _, ending = os.path.splitext(final_path)
        # print(final_path, ending)
        if ending == '.p4p':
            self.search_for_p4pcell(final_path)
        if ending == '.res' or ending == '.ins':
            self.search_for_res_cell(final_path)
        if ending == '.cif':
            self.search_for_cif_cell(final_path)

    @staticmethod
    def validate_sumform(inelem: list):
        """
        Checks if the elements in inelem are valid Chemical elements
        """
        ok = True
        for el in inelem:
            if el not in elements:
                ok = False
        return ok

    @pyqtSlot('QString', name="elements_fields_check")
    def elements_fields_check(self):
        """
        """
        elem1 = self.ui.ad_elementsIncLineEdit.text().split()
        elem2 = self.ui.ad_elementsExclLineEdit.text().split()
        if (not self.elements_doubled_check(elem1, elem2)) or (not self.elements_doubled_check(elem2, elem1)):
            self.elements_invalid()
        else:
            self.elements_regular()

    def elements_doubled_check(self, elem1, elem2):
        """
        Validates if elements of elem1 are not in elem2 and elem1 has purely valid sum formula.
        """
        ok = True
        for el in elem1:
            if el in elem2:
                ok = False
        if not self.validate_sumform(elem1):
            ok = False
        return ok

    def search_csd_and_display_results(self):
        cell = is_valid_cell(self.ui.cellSearchCSDLineEdit.text())
        self.ui.CSDtreeWidget.clear()
        if len(cell) < 6:
            return None
        center = centering_num_2_letter[self.ui.lattCentComboBox.currentIndex()]
        # search the csd:
        xml = search_csd(cell, centering=center)
        try:
            results = parse_results(xml)
        except ParseError as e:
            print(e)
            return
        print(len(results), 'Structures found...')
        self.statusBar().showMessage("{} structures found in the CSD".format(len(results), msecs=9000))
        for res in results:
            csd_tree_item = QTreeWidgetItem()
            self.ui.CSDtreeWidget.addTopLevelItem(csd_tree_item)
            csd_tree_item.setText(0, res['chemical_formula'])
            csd_tree_item.setText(1, res['cell_length_a'])
            csd_tree_item.setText(2, res['cell_length_b'])
            csd_tree_item.setText(3, res['cell_length_c'])
            csd_tree_item.setText(4, res['cell_angle_alpha'])
            csd_tree_item.setText(5, res['cell_angle_beta'])
            csd_tree_item.setText(6, res['cell_angle_gamma'])
            csd_tree_item.setText(7, res['space_group'])
            csd_tree_item.setText(8, res['recid'])
        for n in range(8):
            self.ui.CSDtreeWidget.resizeColumnToContents(n)

    def elements_invalid(self):
        # Elements not valid:
        self.ui.ad_elementsIncLineEdit.setStyleSheet("color: rgb(255, 0, 0); font: bold 12px;")
        self.ui.ad_SearchPushButton.setDisabled(True)
        self.ui.ad_elementsExclLineEdit.setStyleSheet("color: rgb(255, 0, 0); font: bold 12px;")
        self.ui.ad_SearchPushButton.setDisabled(True)

    def elements_regular(self):
        # Elements valid:
        self.ui.ad_elementsIncLineEdit.setStyleSheet("color: rgb(0, 0, 0);")
        self.ui.ad_SearchPushButton.setEnabled(True)
        self.ui.ad_elementsExclLineEdit.setStyleSheet("color: rgb(0, 0, 0);")
        self.ui.ad_SearchPushButton.setEnabled(True)

    def copyUnitCell(self):
        if self.structureId:
            try:
                cell = "{:>6.3f} {:>6.3f} {:>6.3f} {:>6.3f} {:>6.3f} {:>6.3f}" \
                    .format(*self.structures.get_cell_by_id(self.structureId))
                self.ui.cellSearchCSDLineEdit.setText(cell)
            except Exception as e:
                print(e)
                if DEBUG:
                    raise
                return False
            clipboard = QApplication.clipboard()
            clipboard.setText(cell)
            self.ui.statusbar.showMessage('Copied unit cell {} to clip board.'.format(cell))
        return True

    def advanced_search(self):
        """
        Combines all the search fields. Collects all includes, all excludes and calculates
        the difference.
        """
        if not self.structures:
            return
        cell = is_valid_cell(self.ui.ad_unitCellLineEdit.text())
        date1 = self.ui.dateEdit1.text()
        date2 = self.ui.dateEdit2.text()
        elincl = self.ui.ad_elementsIncLineEdit.text().strip(' ')
        elexcl = self.ui.ad_elementsExclLineEdit.text().strip(' ')
        txt = self.ui.ad_textsearch.text().strip(' ')
        if len(txt) >= 2 and "*" not in txt:
            txt = '*' + txt + '*'
        txt_ex = self.ui.ad_textsearch_excl.text().strip(' ')
        if len(txt_ex) >= 2 and "*" not in txt_ex:
            txt_ex = '*' + txt_ex + '*'
        spgr = self.ui.SpGrcomboBox.currentText()
        onlythese = self.ui.onlyTheseElementsCheckBox.isChecked()
        #
        results = []
        cell_results = []
        spgr_results = []
        elincl_results = []
        txt_results = []
        txt_ex_results = []
        date_results = []
        try:
            spgr = int(spgr.split()[0])
        except:
            spgr = 0
        if cell:
            cell_results = self.search_cell_idlist(cell)
        if spgr:
            spgr_results = self.structures.find_by_it_number(spgr)
        if elincl or elexcl:
            elincl_results = self.search_elements(elincl, elexcl, onlythese)
        if txt:
            txt_results = [i[0] for i in self.structures.find_by_strings(txt)]
        if txt_ex:
            txt_ex_results = [i[0] for i in self.structures.find_by_strings(txt_ex)]
        if date1 != date2:
            date_results = self.find_dates(date1, date2)
        ####################
        results = combine_results(cell_results, date_results, elincl_results, results, spgr_results,
                                  txt_ex_results, txt_results)
        self.display_structures_by_idlist(flatten(list(results)))

    def display_structures_by_idlist(self, idlist: list or set) -> None:
        """
        Displays the structures with id in results list
        """
        if not idlist:
            self.statusBar().showMessage('Found {} structures.'.format(0))
            return
        searchresult = self.structures.get_all_structure_names(idlist)
        self.statusBar().showMessage('Found {} structures.'.format(len(idlist)))
        self.ui.cifList_treeWidget.clear()
        self.full_list = False
        for i in searchresult:
            self.add_table_row(name=i[3], path=i[2], structure_id=i[0], data=i[4])
        self.set_columnsize()
        # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        if idlist:
            self.ui.MaintabWidget.setCurrentIndex(0)

    def passwd_handler(self):
        """
        Manages the QDialog buttons on the password dialog.
        """
        d = QDialog()
        self.passwd = self.uipass.setupUi(d)
        ip_dialog = d.exec()
        if ip_dialog == 1:  # Accepted
            self.import_apex_db(user=self.uipass.userNameLineEdit.text(),
                                password=self.uipass.PasswordLineEdit.text(),
                                host=self.uipass.IPlineEdit.text())
        elif ip_dialog == 0:  # reject
            return None
        else:
            return None

    def init_webview(self):
        """
        Initializes a QWebengine to view the molecule.
        """
        self.view = QWebEngineView()
        self.view.load(QUrl.fromLocalFile(os.path.abspath(os.path.join(application_path, "./displaymol/jsmol.htm"))))
        # self.view.setMaximumWidth(260)
        # self.view.setMaximumHeight(290)
        self.view.loadFinished.connect(self.onWebviewLoadFinished)
        self.ui.ogllayout.addWidget(self.view)

    def onWebviewLoadFinished(self):
        self.view.show()

    @pyqtSlot(name="cell_state_changed")
    def cell_state_changed(self):
        """
        Searches a cell but with diffeent loose or strict option.
        """
        self.search_cell(self.ui.searchCellLineEDit.text())

    def import_cif_dirs(self):
        # worker = RunIndexerThread(self)
        # worker.start()
        self.tmpfile = True
        self.statusBar().showMessage('')
        self.close_db()
        self.start_db()
        self.progressbar(1, 0, 20)
        self.abort_import_button.show()
        fname = QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        if not fname:
            self.progress.hide()
            self.abort_import_button.hide()
        filecrawler.put_files_in_db(self, searchpath=fname, fillres=self.ui.add_res.isChecked(),
                                    fillcif=self.ui.add_cif.isChecked())
        self.progress.hide()
        try:
            self.structures.database.init_textsearch()
        except OperationalError as e:
            print(e)
            print('No fulltext search module found.')
        try:
            self.structures.populate_fulltext_search_table()
        except OperationalError as e:
            print(e)
            print('No fulltext search compiled into sqlite.')
        self.structures.database.commit_db()
        self.ui.cifList_treeWidget.show()
        self.set_columnsize()
        # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        # self.ui.cifList_treeWidget.resizeColumnToContents(1)
        # self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.abort_import_button.hide()

    def progressbar(self, curr: int, min: int, max: int) -> None:
        """
        Displays a progress bar in the status bar.
        """
        self.progress.setValue(curr)
        self.progress.setMaximum(max)
        self.progress.setMinimum(min)
        self.progress.show()
        if curr == max:
            self.progress.hide()

    @pyqtSlot(name="close_db")
    def close_db(self, copy_on_close: str = None) -> bool:
        """
        Closed the current database and erases the list.
        copy_on_close is used to save the databse into a file during close_db().
        :param copy_on_close: Path to where the file should be copied after close()
        """
        self.ui.searchCellLineEDit.clear()
        self.ui.txtSearchEdit.clear()
        self.ui.cifList_treeWidget.clear()
        self.write_empty_molfile(mol_data=' ')
        self.view.reload()
        try:
            self.structures.database.cur.close()
        except Exception:
            pass
        try:
            self.structures.database.con.close()
        except Exception:
            pass
        try:
            os.close(self.dbfdesc)
            self.dbfdesc = None
        except:
            pass
        if copy_on_close:
            if isfile(copy_on_close) and samefile(self.dbfilename, copy_on_close):
                self.statusBar().showMessage("You can not save to the currently opened file!", msecs=5000)
                return False
            else:
                shutil.copy(self.dbfilename, copy_on_close)
            if self.tmpfile:
                try:
                    os.remove(self.dbfilename)
                    self.dbfilename = None
                except Exception:
                    return False
        return True

    @pyqtSlot(name="abort_import")
    def abort_import(self):
        """
        This slot means, import was aborted.
        """
        self.decide_import = False

    def start_db(self):
        """
        Initializes the database.
        """
        self.dbfdesc, self.dbfilename = tempfile.mkstemp()
        self.structures = database_handler.StructureTable(self.dbfilename)
        self.structures.database.initialize_db()

    @pyqtSlot('QModelIndex', name="get_properties")
    def get_properties(self, item):
        """
        This slot shows the properties of a cif file in the properties widget
        """
        if not self.structures.database.cur:
            return False
        structure_id = item.sibling(item.row(), 3).data()
        self.structureId = structure_id
        dic = self.structures.get_row_as_dict(structure_id)
        self.display_properties(structure_id, dic)
        self.structureId = structure_id
        return True

    def save_database(self) -> bool:
        """
        Saves the database to a certain file. Therefore I have to close the database.
        """
        status = False
        save_name, tst = QFileDialog.getSaveFileName(self, caption='Save File', directory='./', filter="*.sqlite")
        if save_name:
            if isfile(save_name) and samefile(self.dbfilename, save_name):
                self.statusBar().showMessage("You can not save to the currently opened file!", msecs=5000)
                return False
        if save_name:
            status = self.close_db(save_name)
        if status:
            self.statusBar().showMessage("Database saved.", msecs=5000)

    def eventFilter(self, object, event):
        """Event filter for mouse clicks."""
        if event.type() == QEvent.MouseButtonDblClick:
            self.copyUnitCell()
        elif event.type() == QEvent.MouseButtonPress:
            if event.buttons() == Qt.RightButton:
                # print("rightbutton")
                return True
        return False

    def keyPressEvent(self, q_key_event):
        """
        Event filter for key presses.
        Essentially searches for enter key presses in search fields and runs advanced search.
        """
        if q_key_event.key() == Qt.Key_Return or q_key_event.key() == Qt.Key_Enter:
            fields = [self.ui.ad_elementsExclLineEdit, self.ui.ad_elementsIncLineEdit, self.ui.ad_textsearch,
                      self.ui.ad_textsearch_excl, self.ui.ad_unitCellLineEdit]
            for x in fields:
                if x.hasFocus():
                    self.advanced_search()
        else:
            super().keyPressEvent(q_key_event)

    def redraw_molecule(self):
        cell = self.structures.get_cell_by_id(self.structureId)
        if not cell:
            return False
        try:
            self.display_molecule(cell, str(self.structureId))
        except Exception as e:
            print(e, ", unable to display molecule")
            self.write_empty_molfile(' ')
            self.view.reload()
            if DEBUG:
                raise

    @staticmethod
    def write_empty_molfile(mol_data):
        molf = Path(os.path.join(application_path, "./displaymol/jsmol.htm"))
        molf.write_text(data=mol_data, encoding="utf-8", errors='ignore')

    def display_properties(self, structure_id, cif_dic):
        """
        Displays the residuals from the cif file
        Measured Refl.
        Independent Refl.
        Reflections Used

        _refine_ls_number_reflns -> unique reflect. (Independent reflections)
        _reflns_number_gt        -> unique über 2sigma (Independent reflections >2sigma)
        """
        self.clear_fields()
        cell = self.structures.get_cell_by_id(structure_id)
        if self.ui.cellSearchCSDLineEdit.isEnabled() and cell:
            self.ui.cellSearchCSDLineEdit.setText("  ".join([str(round(x, 5)) for x in cell[:6]]))
            try:
                cstring = cif_dic['_space_group_centring_type']
                self.ui.lattCentComboBox.setCurrentIndex(centering_letter_2_num[cstring])
            except (KeyError, TypeError):
                pass
        if not cell:
            return False
        try:
            self.display_molecule(cell, structure_id)
        except Exception as e:
            print(e, "unable to display molecule!!")
            self.write_empty_molfile(mol_data=' ')
            self.view.reload()
            if DEBUG:
                raise
        self.ui.cifList_treeWidget.setFocus()
        if not cif_dic:
            return False
        a, b, c, alpha, beta, gamma, volume = 0, 0, 0, 0, 0, 0, 0
        if cell:
            a, b, c, alpha, beta, gamma, volume = cell[0], cell[1], cell[2], cell[3], cell[4], cell[5], cell[6]
        if not all((a, b, c, alpha, beta, gamma, volume)):
            self.ui.cellField.setText('            ')
            return False
        # self.ui.cellField.setMinimumWidth(180)
        try:
            cent = cif_dic['_space_group_centring_type']
        except KeyError:
            cent = ''
        self.ui.cellField.setText(constants.celltxt.format(a, alpha, b, beta, c, gamma, volume, cent))
        self.ui.cellField.installEventFilter(self)
        self.ui.cellField.setToolTip("Double click on 'Unit Cell' to copy to clipboard.")
        try:
            self.ui.wR2LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_wR_factor_ref']))
        except (ValueError, TypeError):
            pass
        try:  # R1:
            if cif_dic['_refine_ls_R_factor_gt']:
                self.ui.r1LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_R_factor_gt']))
            else:
                self.ui.r1LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_R_factor_all']))
        except (ValueError, TypeError):
            pass
        self.ui.zLineEdit.setText("{}".format(cif_dic['_cell_formula_units_Z']))
        try:
            sumform = misc.format_sum_formula(self.structures.get_calc_sum_formula(structure_id))
        except KeyError:
            sumform = ''
        if sumform == '':
            # Display this as last resort:
            sumform = cif_dic['_chemical_formula_sum']
        self.ui.SumformLabel.setMinimumWidth(self.ui.reflTotalLineEdit.width())
        self.ui.SumformLabel.setText("{}".format(sumform))
        self.ui.reflTotalLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_number']))
        self.ui.uniqReflLineEdit.setText("{}".format(cif_dic['_refine_ls_number_reflns']))
        self.ui.refl2sigmaLineEdit.setText("{}".format(cif_dic['_reflns_number_gt']))
        self.ui.goofLineEdit.setText("{}".format(cif_dic['_refine_ls_goodness_of_fit_ref']))
        it_num = cif_dic['_space_group_IT_number']
        if it_num:
            it_num = "({})".format(it_num)
        self.ui.SpaceGroupLineEdit.setText("{} {}".format(cif_dic['_space_group_name_H_M_alt'], it_num))
        self.ui.temperatureLineEdit.setText("{}".format(cif_dic['_diffrn_ambient_temperature']))
        self.ui.maxShiftLineEdit.setText("{}".format(cif_dic['_refine_ls_shift_su_max']))
        peak = cif_dic['_refine_diff_density_max']
        if peak:
            self.ui.peakLineEdit.setText("{} / {}".format(peak, cif_dic['_refine_diff_density_min']))
        self.ui.rintLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_av_R_equivalents']))
        self.ui.rsigmaLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_av_unetI_netI']))
        self.ui.cCDCNumberLineEdit.setText("{}".format(cif_dic['_database_code_depnum_ccdc_archive']))
        try:
            dat_param = cif_dic['_refine_ls_number_reflns'] / cif_dic['_refine_ls_number_parameters']
        except (ValueError, ZeroDivisionError, TypeError):
            dat_param = 0.0
        self.ui.dataReflnsLineEdit.setText("{:<5.1f}".format(dat_param))
        self.ui.numParametersLineEdit.setText("{}".format(cif_dic['_refine_ls_number_parameters']))
        wavelen = cif_dic['_diffrn_radiation_wavelength']
        thetamax = cif_dic['_diffrn_reflns_theta_max']
        # d = lambda/2sin(theta):
        try:
            d = wavelen / (2 * math.sin(math.radians(thetamax)))
        except(ZeroDivisionError, TypeError):
            d = 0.0
        self.ui.numRestraintsLineEdit.setText("{}".format(cif_dic['_refine_ls_number_restraints']))
        self.ui.thetaMaxLineEdit.setText("{}".format(thetamax))
        self.ui.thetaFullLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_theta_full']))
        self.ui.dLineEdit.setText("{:5.3f}".format(d))
        self.ui.lastModifiedLineEdit.setText(cif_dic['modification_time'])
        try:
            compl = cif_dic['_diffrn_measured_fraction_theta_max'] * 100
            if not compl:
                compl = 0.0
        except TypeError:
            compl = 0.0
        try:
            self.ui.completeLineEdit.setText("{:<5.1f}".format(compl))
        except ValueError:
            pass
        self.ui.wavelengthLineEdit.setText("{}".format(wavelen))
        self.ui.allCifTreeWidget.clear()
        # This makes selection slow and is not really needed:
        # atoms_item = QtWidgets.QTreeWidgetItem()
        for key, value in cif_dic.items():
            if key == "_shelx_res_file":
                self.ui.SHELXplainTextEdit.setPlainText(cif_dic['_shelx_res_file'])
                continue
            cif_tree_item = QTreeWidgetItem()
            self.ui.allCifTreeWidget.addTopLevelItem(cif_tree_item)
            cif_tree_item.setText(0, str(key))
            cif_tree_item.setText(1, str(value))
        if not cif_dic['_shelx_res_file']:
            self.ui.SHELXplainTextEdit.setPlainText("No SHELXL res file in cif found.")
        # self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.ui.allCifTreeWidget.resizeColumnToContents(0)
        self.ui.allCifTreeWidget.resizeColumnToContents(1)
        return True

    def display_molecule(self, cell: list, structure_id: str) -> None:
        """
        Creates a html file from a mol file to display the molecule in jsmol-lite
        """
        symmcards = [x.split(',') for x in self.structures.get_row_as_dict(structure_id)
        ['_space_group_symop_operation_xyz'].replace("'", "").replace(" ", "").split("\n")]
        if symmcards[0] == ['']:
            print('Cif file has no symmcards, unable to grow structure.')
        blist = []
        if self.ui.growCheckBox.isChecked():
            self.ui.molGroupBox.setTitle('Completed Molecule')
            atoms = self.structures.get_atoms_table(structure_id, cell[:6], cartesian=False, as_list=True)
            if atoms:
                sdm = SDM(atoms, symmcards, cell)
                needsymm = sdm.calc_sdm()
                atoms = sdm.packer(sdm, needsymm)
                # blist = [(x[0]+1, x[1]+1) for x in sdm.bondlist]
                # print(len(blist))
        else:
            self.ui.molGroupBox.setTitle('Asymmetric Unit')
            atoms = self.structures.get_atoms_table(structure_id, cell[:6], cartesian=True, as_list=False)
            blist = []
        try:
            mol = ' '
            if atoms:
                mol = mol_file_writer.MolFile(atoms, blist)
                mol = mol.make_mol()
        except (TypeError, KeyError):
            print("Error in structure", structure_id, "while writing mol file.")
            mol = ' '
            if DEBUG:
                raise
        # print(self.ui.openglview.width()-30, self.ui.openglview.height()-50)
        content = write_html.write(mol, self.ui.openglview.width() - 30, self.ui.openglview.height() - 50)
        p2 = Path(os.path.join(application_path, "./displaymol/jsmol.htm"))
        p2.write_text(data=content, encoding="utf-8", errors='ignore')
        self.view.reload()

    @pyqtSlot('QString')
    def find_dates(self, date1: str, date2: str) -> list:
        """
        Returns a list if id between date1 and date2
        """
        if not date1:
            date1 = '0000-01-01'
        if not date2:
            date2 = 'NOW'
        result = self.structures.find_by_date(date1, date2)
        return result

    @pyqtSlot('QString')
    def search_text(self, search_string: str) -> bool:
        """
        searches db for given text
        """
        self.ui.searchCellLineEDit.clear()
        self.ui.cifList_treeWidget.clear()
        try:
            if not self.structures:
                return False  # Empty database
        except:
            return False  # No database cursor
        idlist = []
        if len(search_string) == 0:
            self.show_full_list()
            return False
        if len(search_string) >= 2 and "*" not in search_string:
            search_string = "{}{}{}".format('*', search_string, '*')
        try:
            idlist = self.structures.find_by_strings(search_string)
        except AttributeError as e:
            print(e)
        try:
            self.statusBar().showMessage("Found {} entries.".format(len(idlist)))
            for i in idlist:
                self.add_table_row(name=i[1], path=i[3], structure_id=i[0], data=i[2])
            self.set_columnsize()
            # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        except Exception:
            self.statusBar().showMessage("Nothing found.")

    def search_cell_idlist(self, cell: list) -> list:
        """
        Searches for a unit cell and resturns a list of found database ids.
        This method does not validate the cell. This has to be done before!
        """
        if self.ui.moreResultsCheckBox.isChecked() or self.ui.ad_moreResultscheckBox.isChecked():
            # more results:
            vol_threshold = 0.09
            ltol = 0.2
            atol = 2
        else:
            # regular:
            vol_threshold = 0.03
            ltol = 0.06
            atol = 1
        try:
            volume = lattice.vol_unitcell(*cell)
            idlist = self.structures.find_by_volume(volume, vol_threshold)
            if self.ui.sublattCheckbox.isChecked() or self.ui.ad_superlatticeCheckBox.isChecked():
                # sub- and superlattices:
                for v in [volume * x for x in [2.0, 3.0, 4.0, 6.0, 8.0, 10.0]]:
                    # First a list of structures where the volume is similar:
                    idlist.extend(self.structures.find_by_volume(v, vol_threshold))
                idlist = list(set(idlist))
                idlist.sort()
        except (ValueError, AttributeError):
            if not self.full_list:
                self.ui.cifList_treeWidget.clear()
                self.statusBar().showMessage('Found 0 cells.')
            return []
        # Real lattice comparing in G6:
        idlist2 = []
        if idlist:
            lattice1 = mat_lattice.Lattice.from_parameters_niggli_reduced(*cell)
            self.statusBar().clearMessage()
            cells = []
            # SQLite can only handle 999 variables at once:
            for cids in chunks(idlist, 500):
                cells.extend(self.structures.get_cells_as_list(cids))
            for num, cell_id in enumerate(idlist):
                self.progressbar(num, 0, len(idlist) - 1)
                try:
                    lattice2 = mat_lattice.Lattice.from_parameters(*cells[num][:6])
                except ValueError:
                    continue
                mapping = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
                if mapping:
                    # pprint.pprint(map[3])
                    idlist2.append(cell_id)
        # print("After match: ", len(idlist2))
        return idlist2

    @pyqtSlot('QString', name='search_cell')
    def search_cell(self, search_string: str) -> bool:
        """
        searches db for given cell via the cell volume
        """
        cell = is_valid_cell(search_string)
        self.ui.ad_unitCellLineEdit.setText('  '.join([str(x) for x in cell]))
        if self.ui.cellSearchCSDLineEdit.isEnabled() and cell:
            self.ui.cellSearchCSDLineEdit.setText('  '.join([str(x) for x in cell]))
        self.ui.txtSearchEdit.clear()
        if not cell:
            if str(self.ui.searchCellLineEDit.text()):
                self.statusBar().showMessage('Not a valid unit cell!', msecs=3000)
                return False
            else:
                self.full_list = True  # Set status where full list is displayed
                self.show_full_list()
            if self.full_list:
                return False
            return False
        try:
            if not self.structures:
                return False  # Empty database
        except Exception:
            return False  # No database cursor
        idlist = self.search_cell_idlist(cell)
        if not idlist:
            self.ui.cifList_treeWidget.clear()
            self.statusBar().showMessage('Found 0 cells.', msecs=0)
            return False
        searchresult = self.structures.get_all_structure_names(idlist)
        self.statusBar().showMessage('Found {} cells.'.format(len(idlist)))
        self.ui.cifList_treeWidget.clear()
        self.full_list = False
        for i in searchresult:
            self.add_table_row(name=i[3], path=i[2], structure_id=i[0], data=i[4])
            # self.add_table_row(name, path, id)
        self.set_columnsize()
        # self.ui.cifList_treeWidget.sortByColumn(0, 0)
        # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        return True

    def search_elements(self, elements: str, excluding: str, onlythese: bool = False) -> list:
        """
        list(set(l).intersection(l2))
        """
        self.statusBar().showMessage('')
        res = []
        try:
            formula = misc.get_list_of_elements(elements)
        except KeyError:
            self.statusBar().showMessage('Error: Wrong list of Elements!', msecs=5000)
            return []
        try:
            formula_ex = misc.get_list_of_elements(excluding)
        except KeyError:
            self.statusBar().showMessage('Error: Wrong list of Elements!', msecs=5000)
            return []
        try:
            res = self.structures.find_by_elements(formula, excluding=formula_ex, onlyincluded=onlythese)
        except AttributeError:
            pass
        return list(res)

    def add_table_row(self, name: str, path: str, data: bytes, structure_id: str) -> None:
        """
        Adds a line to the search results table.
        """
        if isinstance(name, bytes):
            name = name.decode("utf-8", "surrogateescape")
        if isinstance(path, bytes):
            path = path.decode("utf-8", "surrogateescape")
        if isinstance(data, bytes):
            data = data.decode("utf-8", "surrogateescape")
        tree_item = QTreeWidgetItem()
        tree_item.setText(0, name)  # name
        tree_item.setText(1, data)  # data
        tree_item.setText(2, path)  # path
        tree_item.setData(3, 0, structure_id)  # id
        self.ui.cifList_treeWidget.addTopLevelItem(tree_item)

    def import_cif_database(self) -> bool:
        """
        Import a new database.
        """
        self.tmpfile = False
        self.close_db()
        fname = QFileDialog.getOpenFileName(self, caption='Open File', directory='./', filter="*.sqlite")
        if not fname[0]:
            return False
        print("Opened {}.".format(fname[0]))
        self.dbfilename = fname[0]
        self.structures = database_handler.StructureTable(self.dbfilename)
        try:
            self.show_full_list()
        except DatabaseError:
            self.moving_message('Database file is corrupt!')
            self.close_db()
            return False
        try:
            if self.structures:
                pass
        except (TypeError, ProgrammingError):
            return False
        return True

    def open_apex_db(self, user: str, password: str, host: str) -> bool:
        """
        Opens the APEX db to be displayed in the treeview.
        """
        self.apx = apeximporter.ApexDB()
        connok = False
        try:
            connok = self.apx.initialize_db(user, password, host)
        except Exception:
            self.passwd_handler()
        return connok

    def get_name_from_p4p(self):
        """
        Reads a p4p file to get the included unit cell for a cell search.
        """
        fname, _ = QFileDialog.getOpenFileName(self, caption='Open p4p File', directory='./',
                                               filter="*.p4p *.cif *.res *.ins")
        fname = str(fname)
        _, ending = os.path.splitext(fname)
        if ending == '.p4p':
            self.search_for_p4pcell(fname)
        if ending in ['.res', '.ins']:
            self.search_for_res_cell(fname)
        if ending == '.cif':
            self.search_for_cif_cell(fname)

    def search_for_p4pcell(self, fname):
        if fname:
            p4plist = read_file_to_list(fname)
            p4p = P4PFile(p4plist)
        else:
            return
        if p4p:
            if p4p.cell:
                try:
                    self.ui.searchCellLineEDit.setText('{:<6.3f} {:<6.3f} {:<6.3f} '
                                                       '{:<6.3f} {:<6.3f} {:<6.3f}'.format(*p4p.cell))
                except TypeError:
                    pass
            else:
                self.moving_message('Could not read P4P file!')
        else:
            self.moving_message('Could not read P4P file!')

    def search_for_res_cell(self, fname):
        if fname:
            shx = ShelXFile(fname)
        else:
            return
        if shx:
            if shx.cell:
                try:
                    self.ui.searchCellLineEDit.setText('{:<6.3f} {:<6.3f} {:<6.3f} '
                                                       '{:<6.3f} {:<6.3f} {:<6.3f}'.format(*shx.cell))
                except TypeError:
                    pass
            else:
                self.moving_message('Could not read res file!')
        else:
            self.moving_message('Could not read res file!')

    def search_for_cif_cell(self, fname):
        if fname:
            cif = Cif()
            try:
                cif.parsefile(Path(fname).read_text(encoding='utf-8',
                                                    errors='ignore').splitlines(keepends=True))
            except FileNotFoundError:
                self.moving_message('File not found.')
        else:
            return
        if cif:
            if cif.cell:
                try:
                    self.ui.searchCellLineEDit.setText('{:<6.3f} {:<6.3f} {:<6.3f} '
                                                       '{:<6.3f} {:<6.3f} {:<6.3f}'.format(*cif.cell[:6]))
                except TypeError:
                    pass
            else:
                self.moving_message('Could not read cif file!')
        else:
            self.moving_message('Could not read cif file!')

    def moving_message(self, message="", times=20):
        for s in range(times):
            time.sleep(0.05)
            self.statusBar().showMessage("{}{}".format(' ' * s, message))

    def import_apex_db(self, user: str = '', password: str = '', host: str = '') -> None:
        """
        Imports data from apex into own db
        """
        self.statusBar().showMessage('')
        self.close_db()
        self.start_db()
        self.ui.cifList_treeWidget.show()
        self.abort_import_button.show()
        n = 1
        num = 0
        time1 = time.perf_counter()
        conn = self.open_apex_db(user, password, host)
        if not conn:
            self.abort_import_button.hide()
            return None
        cif = Cif()
        if conn:
            for i in self.apx.get_all_data():
                if num == 20:
                    num = 0
                self.progressbar(num, 0, 20)
                cif.cif_data['_cell_length_a'] = i[1]
                cif.cif_data['_cell_length_b'] = i[2]
                cif.cif_data['_cell_length_c'] = i[3]
                cif.cif_data['_cell_angle_alpha'] = i[4]
                cif.cif_data['_cell_angle_beta'] = i[5]
                cif.cif_data['_cell_angle_gamma'] = i[6]
                cif.cif_data["data"] = i[8]
                cif.cif_data['_diffrn_radiation_wavelength'] = i[13]
                cif.cif_data['_exptl_crystal_colour'] = i[29]
                cif.cif_data['_exptl_crystal_size_max'] = i[16]
                cif.cif_data['_exptl_crystal_size_mid'] = i[17]
                cif.cif_data['_exptl_crystal_size_min'] = i[18]
                cif.cif_data["_chemical_formula_sum"] = i[25]
                cif.cif_data['_diffrn_reflns_av_R_equivalents'] = i[21]  # rint
                cif.cif_data['_diffrn_reflns_av_unetI/netI'] = i[22]  # rsig
                cif.cif_data['_diffrn_reflns_number'] = i[23]
                comp = i[26]
                cif.cif_data["_space_group_centring_type"] = i[28]
                if comp:
                    cif.cif_data['_diffrn_measured_fraction_theta_max'] = comp / 100
                tst = filecrawler.fill_db_tables(cif=cif, filename=i[8], path=i[12],
                                                 structure_id=n, structures=self.structures)
                if not tst:
                    continue
                self.add_table_row(name=i[8], data=i[8], path=i[12], structure_id=str(n))
                n += 1
                if n % 300 == 0:
                    self.structures.database.commit_db()
                num += 1
                if not self.decide_import:
                    # This means, import was aborted.
                    self.abort_import_button.hide()
                    self.decide_import = True
                    break
        time2 = time.perf_counter()
        diff = time2 - time1
        self.progress.hide()
        m, s = divmod(diff, 60)
        h, m = divmod(m, 60)
        if n == 0:
            n += 1
        self.ui.statusbar.showMessage('Added {} APEX entries in: {:>2d} h, {:>2d} m, {:>3.2f} s'
                                      .format(n - 1, int(h), int(m), s), msecs=0)
        # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        self.set_columnsize()
        self.structures.database.init_textsearch()
        self.structures.populate_fulltext_search_table()
        self.structures.database.commit_db("Committed")
        self.abort_import_button.hide()

    def set_columnsize(self):
        """
        Sets columnsize of main structure list.
        """
        self.ui.cifList_treeWidget.sortByColumn(0, 0)
        treewidth = self.ui.cifList_treeWidget.width()
        self.ui.cifList_treeWidget.setColumnWidth(0, treewidth / 4)
        self.ui.cifList_treeWidget.setColumnWidth(1, treewidth / 5)
        # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        # self.ui.cifList_treeWidget.resizeColumnToContents(1)

    def show_full_list(self) -> None:
        """
        Displays the complete list of structures
        [structure_id, meas, path, filename, data]
        """
        self.ui.cifList_treeWidget.clear()
        structure_id = 0
        try:
            if self.structures:
                pass
        except TypeError:
            return None
        if self.structures:
            for i in self.structures.get_all_structure_names():
                structure_id = i[0]
                self.add_table_row(name=i[3], path=i[2], structure_id=i[0], data=i[4])
        mess = "Loaded {} entries.".format(structure_id)
        self.statusBar().showMessage(mess, msecs=5000)
        self.set_columnsize()
        # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        # self.ui.cifList_treeWidget.resizeColumnToContents(1)
        self.full_list = True
        self.ui.MaintabWidget.setCurrentIndex(0)
        self.ui.SpGrcomboBox.setCurrentIndex(0)
        self.ui.ad_elementsIncLineEdit.clear()
        self.ui.ad_elementsExclLineEdit.clear()
        self.ui.ad_moreResultscheckBox.setChecked(False)
        self.ui.ad_superlatticeCheckBox.setChecked(False)
        self.ui.ad_textsearch.clear()
        self.ui.ad_textsearch_excl.clear()
        self.ui.ad_unitCellLineEdit.clear()
        self.ui.dateEdit1.setDate(QDate(date.today()))
        self.ui.dateEdit2.setDate(QDate(date.today()))

    def clear_fields(self) -> None:
        """
        Clears all residuals fields.
        """
        self.ui.completeLineEdit.clear()
        self.ui.dataReflnsLineEdit.clear()
        self.ui.dLineEdit.clear()
        self.ui.goofLineEdit.clear()
        self.ui.maxShiftLineEdit.clear()
        self.ui.numParametersLineEdit.clear()
        self.ui.numRestraintsLineEdit.clear()
        self.ui.peakLineEdit.clear()
        self.ui.r1LineEdit.clear()
        self.ui.reflTotalLineEdit.clear()
        self.ui.rintLineEdit.clear()
        self.ui.rsigmaLineEdit.clear()
        self.ui.SpaceGroupLineEdit.clear()
        self.ui.SumformLabel.clear()
        self.ui.temperatureLineEdit.clear()
        self.ui.thetaFullLineEdit.clear()
        self.ui.thetaMaxLineEdit.clear()
        self.ui.wavelengthLineEdit.clear()
        self.ui.wR2LineEdit.clear()
        self.ui.zLineEdit.clear()
        self.ui.cCDCNumberLineEdit.clear()
        self.ui.refl2sigmaLineEdit.clear()
        self.ui.uniqReflLineEdit.clear()
        self.ui.lastModifiedLineEdit.clear()
        self.ui.SHELXplainTextEdit.clear()


if __name__ == "__main__":
    from PyQt5 import uic
    try:
        uic.compileUiDir(os.path.join(application_path, './gui'))
    except:
        print("Unable to compile UI!")
        raise
    from gui.strf_main import Ui_stdbMainwindow
    from gui.strf_dbpasswd import Ui_PasswdDialog

    # later http://www.pyinstaller.org/
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./icons/strf.png'))
    # Has to be without version number, because QWebengine stores data in ApplicationName directory:
    app.setApplicationName('StructureFinder')
    # app.setApplicationDisplayName("StructureFinder")
    myapp = StartStructureDB()
    myapp.show()
    myapp.raise_()
    myapp.setWindowTitle('StructureFinder v{}'.format(VERSION))
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit()
