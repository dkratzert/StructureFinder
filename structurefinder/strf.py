#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <dkratzert@gmx.de> wrote this file. As long as you retain this
* notice you can do whatever you want with this stuff. If we meet some day, and
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: Daniel Kratzert
"""
import os
import shutil
import sys
import tempfile
import time
import traceback
from contextlib import suppress
from datetime import date
from math import sin, radians
from os.path import isfile, samefile
from pathlib import Path
from sqlite3 import DatabaseError, ProgrammingError, OperationalError
from typing import Union

from PyQt5 import QtGui
from PyQt5.QtCore import QModelIndex, pyqtSlot, QDate, QEvent, Qt, QItemSelection, QThread
from PyQt5.QtWidgets import QApplication, QFileDialog, QProgressBar, QTreeWidgetItem, QMainWindow, \
    QMessageBox, QPushButton

from structurefinder.displaymol.sdm import SDM
from structurefinder.gui.table_model import TableModel
from structurefinder.misc.dialogs import bug_found_warning, do_update_program
from structurefinder.misc.download import MyDownloader
from structurefinder.misc.exporter import export_to_cif_file
from structurefinder.misc.settings import StructureFinderSettings
from structurefinder.p4pfile.p4p_reader import P4PFile, read_file_to_list
from structurefinder.searcher import database_handler, constants
from structurefinder.searcher.worker import Worker
from structurefinder.shelxfile.shelx import ShelXFile

app = QApplication(sys.argv)

print(sys.version)
DEBUG = False

from structurefinder.misc.version import VERSION
from structurefinder.pymatgen.core import lattice
from structurefinder.searcher import misc
from structurefinder.searcher.constants import centering_num_2_letter, centering_letter_2_num
from structurefinder.searcher.fileparser import Cif
from structurefinder.searcher.misc import is_valid_cell, elements, combine_results, more_results_parameters, \
    regular_results_parameters

is_windows = False
import platform

if platform.system() == 'Windows':
    is_windows = True

try:
    from xml.etree.ElementTree import ParseError
    from structurefinder.ccdc.query import get_cccsd_path, search_csd, parse_results
except ModuleNotFoundError:
    print('Non xml parser found.')

"""
TODO:
- Use ultra fast file walk for Windows:
  https://github.com/githubrobbi/Ultra-Fast-Walk-in-NIM
  nim c -d:danger --app:lib --opt:speed --gc:markAndSweep --out:ultra_fast_walk.pyd ultra_fast_walk.nim
  import ultra_fast_walk as ufw
  p = ufw.walker(folderpath= "C:/", extensions=[".res"], yieldfiles=False)
- add options
- Use spellfix for text search: https://www.sqlite.org/spellfix1.html

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

if DEBUG:
    try:
        from PyQt5 import uic, QtGui

        uic.compileUiDir(os.path.join(application_path, 'gui'))
        print('recompiled ui')
    except:
        print("Unable to compile UI!")
        raise
else:
    print("Remember, UI is not recompiled without DEBUG.")

from structurefinder.gui.strf_main import Ui_stdbMainwindow


class StartStructureDB(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setStyleHint(QtGui.QFont.Monospace)
        self.ui.SHELXplainTextEdit.setFont(font)
        self.statusBar().showMessage('StructureFinder version {}'.format(VERSION))
        self.maxfiles = 0
        self.dbfdesc = None
        self.dbfilename = None
        self.tmpfile = False  # indicates wether a tmpfile or any other db file is used
        self.abort_import_button = QPushButton('Abort Indexing')
        self.progress = QProgressBar(self)
        self.progress.setFormat('')
        self.ui.statusbar.addWidget(self.progress)
        self.ui.appendDirButton.setDisabled(True)
        self.ui.statusbar.addWidget(self.abort_import_button)
        self.structures = None
        self.apx = None
        self.structureId = 0
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
        self.ui.dateEdit1.setDate(QDate(date.today()))
        self.ui.dateEdit2.setDate(QDate(date.today()))
        self.ui.MaintabWidget.setCurrentIndex(0)
        self.setWindowIcon(QtGui.QIcon(os.path.join(application_path, '../icons/strf.png')))
        # Actions for certain gui elements:
        self.ui.cellField.addAction(self.ui.actionCopy_Unit_Cell)
        # self.ui.cifList_tableView.addAction(self.ui.actionGo_to_All_CIF_Tab)
        self.settings = StructureFinderSettings()
        if len(sys.argv) > 1:
            self.dbfilename = sys.argv[1]
            if isfile(self.dbfilename):
                try:
                    self.structures = database_handler.StructureTable(self.dbfilename)
                    self.show_full_list()
                    self.ui.appendDirButton.setEnabled(True)
                except (IndexError, DatabaseError) as e:
                    print(e)
                    if DEBUG:
                        raise
                os.chdir(str(Path(self.dbfilename).parent))
                self.ui.DatabaseNameDisplayLabel.setText('Database opened: {}'.format(self.dbfilename))
                self.settings.save_current_dir(str(Path(self.dbfilename).parent))
                self.display_number_of_structures()
        else:
            lastdir = self.settings.load_last_workdir()
            if Path(lastdir).exists():
                with suppress(OSError, FileNotFoundError):
                    os.chdir(self.settings.load_last_workdir())
        if self.structures:
            self.set_model_from_data(self.structures.get_all_structure_names())
        self.ui.SumformLabel.setMinimumWidth(self.ui.reflTotalLineEdit.width())
        if not "PYTEST_CURRENT_TEST" in os.environ:
            self.checkfor_version()

    def set_model_from_data(self, data: Union[list, tuple]):
        self.table_model = TableModel(structures=data)
        self.ui.cifList_tableView.setModel(self.table_model)
        self.ui.cifList_tableView.hideColumn(0)
        self.ui.cifList_tableView.selectionModel().selectionChanged.connect(self.get_properties)
        # self.ui.cifList_tableView.resizeColumnToContents(1)
        # self.ui.cifList_tableView.resizeColumnToContents(2)
        self.ui.cifList_tableView.resizeColumnToContents(3)

    def connect_signals_and_slots(self):
        """
        Connects the signals and slot.
        The actionExit signal is connected in the ui file.
        """
        # Buttons:
        self.ui.importDatabaseButton.clicked.connect(self.open_database_file)
        self.ui.saveDatabaseButton.clicked.connect(self.save_database)
        self.ui.importDirButton.clicked.connect(self.import_file_dirs)
        self.ui.appendDirButton.clicked.connect(self.append_file_dirs)
        self.ui.closeDatabaseButton.clicked.connect(self.close_db)
        # self.abort_import_button.clicked.connect(self.abort_import)
        self.ui.moreResultsCheckBox.stateChanged.connect(self.cell_state_changed)
        self.ui.sublattCheckbox.stateChanged.connect(self.cell_state_changed)
        self.ui.adv_SearchPushButton.clicked.connect(self.advanced_search)
        self.ui.adv_ClearSearchButton.clicked.connect(self.show_full_list)
        if is_windows:
            self.ui.CSDpushButton.clicked.connect(self.search_csd_and_display_results)
        # Actions:
        self.ui.actionClose_Database.triggered.connect(self.close_db)
        self.ui.actionImport_directory.triggered.connect(self.import_file_dirs)
        self.ui.actionImport_file.triggered.connect(self.open_database_file)
        self.ui.actionSave_Database.triggered.connect(self.save_database)
        self.ui.actionCopy_Unit_Cell.triggered.connect(self.copyUnitCell)
        self.ui.cifList_tableView.save_excel_triggered.connect(self.on_save_as_excel)
        # Other fields:
        self.ui.txtSearchEdit.textChanged.connect(self.search_text)
        self.ui.searchCellLineEDit.textChanged.connect(self.search_cell)
        self.ui.p4pCellButton.clicked.connect(self.get_name_from_p4p)
        ##self.ui.cifList_treeWidget.itemDoubleClicked.connect(self.on_click_item)
        self.ui.CSDtreeWidget.itemDoubleClicked.connect(self.show_csdentry)
        self.ui.adv_elementsIncLineEdit.textChanged.connect(self.elements_fields_check)
        self.ui.adv_elementsExclLineEdit.textChanged.connect(self.elements_fields_check)
        self.ui.add_res.clicked.connect(self.res_checkbox_clicked)
        self.ui.add_cif.clicked.connect(self.cif_checkbox_clicked)
        self.ui.growCheckBox.toggled.connect(self.redraw_molecule)
        self.ui.ExportAsCIFpushButton.clicked.connect(self.export_current_cif)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(StartStructureDB, self).resizeEvent(a0)

    def checkfor_version(self):
        url = 'https://dkratzert.de/files/structurefinder/version.txt'
        upd = MyDownloader(self, url)
        upd.finished.connect(self.show_update_warning)
        upd.failed.connect(upd.failed_to_download)
        upd.progress.connect(upd.print_status)
        upd.start()

    def show_update_warning(self, reply: bytes):
        """
        Reads the reply from the server and displays a warning in case of an old version.
        """
        remote_version = 0
        try:
            remote_version = int(reply.decode('ascii', 'ignore'))
        except Exception:
            pass
        if remote_version > VERSION:
            print('Version {} is outdated (actual is {}).'.format(remote_version, VERSION))
            warn_text = "A newer version of StructureFinder is available under " \
                        "<a href='https://dkratzert.de/structurefinder.html'>" \
                        "https://dkratzert.de/structurefinder.html</a>"
            box = QMessageBox()
            box.setTextFormat(Qt.AutoText)
            box.setWindowTitle(" ")
            box.setTextInteractionFlags(Qt.TextBrowserInteraction)
            if sys.platform.startswith("win"):
                warn_text += r"<br><br>Updating now will end all running StructureFinder programs!"
                update_button = box.addButton('Update Now', QMessageBox.AcceptRole)
                update_button.clicked.connect(lambda: do_update_program(str(remote_version)))
            box.setText(warn_text.format(remote_version))
            box.exec()

    def res_checkbox_clicked(self, click):
        if not any([self.ui.add_res.isChecked(), self.ui.add_cif.isChecked()]):
            self.ui.add_res.setChecked(True)

    def cif_checkbox_clicked(self, click):
        if not any([self.ui.add_res.isChecked(), self.ui.add_cif.isChecked()]):
            self.ui.add_cif.setChecked(True)

    def on_save_as_excel(self):
        # filename = '/Users/daniel/Documents/GitHub/StructureFinder/test.xlsx'
        filename = self.get_excel_export_filename_from_dialog()
        if not filename or Path(filename).is_dir():
            return None
        selection = self.ui.cifList_tableView.selectionModel().selectedRows()
        self.write_excel_file_from_selection(filename, selection)
        self.ui.statusbar.showMessage(f'Selected rows written to {filename}')

    def write_excel_file_from_selection(self, filename, selection):
        import xlsxwriter
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        for row, index in enumerate(selection):
            row_data = self.ui.cifList_tableView.model()._data[index.row()]
            for col, item in enumerate(row_data):
                worksheet.write(row, col, item.decode('utf-8') if isinstance(item, bytes) else item)
        workbook.close()

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
        elem1 = self.ui.adv_elementsIncLineEdit.text().split()
        elem2 = self.ui.adv_elementsExclLineEdit.text().split()
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
        self.statusBar().showMessage(f"{len(results)} structures found in the CSD", msecs=9000)
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
        self.ui.adv_elementsIncLineEdit.setStyleSheet("color: rgb(255, 0, 0); font: bold 12px;")
        self.ui.adv_SearchPushButton.setDisabled(True)
        self.ui.adv_elementsExclLineEdit.setStyleSheet("color: rgb(255, 0, 0); font: bold 12px;")
        self.ui.adv_SearchPushButton.setDisabled(True)

    def elements_regular(self):
        # Elements valid:
        self.ui.adv_elementsIncLineEdit.setStyleSheet("color: rgb(0, 0, 0);")
        self.ui.adv_SearchPushButton.setEnabled(True)
        self.ui.adv_elementsExclLineEdit.setStyleSheet("color: rgb(0, 0, 0);")
        self.ui.adv_SearchPushButton.setEnabled(True)

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
        self.clear_fields()
        states = {'date'  : False,
                  'cell'  : False,
                  'elincl': False,
                  'elexcl': False,
                  'txt'   : False,
                  'txt_ex': False,
                  'spgr'  : False,
                  'rval'  : False,
                  'ccdc'  : False}
        if not self.structures:
            return
        cell = is_valid_cell(self.ui.adv_unitCellLineEdit.text())
        date1 = self.ui.dateEdit1.text()
        date2 = self.ui.dateEdit2.text()
        elincl = self.ui.adv_elementsIncLineEdit.text().strip(' ')
        elexcl = self.ui.adv_elementsExclLineEdit.text().strip(' ')
        txt = self.ui.adv_textsearch.text().strip(' ')
        ccdc_num = self.ui.CCDCNumLineEdit.text().strip(' ')
        try:
            rval = float(self.ui.adv_R1_search_line.text().strip(' '))
            states['rval'] = True
        except ValueError:
            rval = 0
        if len(txt) >= 2 and "*" not in txt:
            txt = '*' + txt + '*'
        txt_ex = self.ui.adv_textsearch_excl.text().strip(' ')
        if len(txt_ex) >= 2 and "*" not in txt_ex:
            txt_ex = '*' + txt_ex + '*'
        spgr = self.ui.SpGrpComboBox.currentText()
        onlythese = self.ui.onlyTheseElementsCheckBox.isChecked()
        #
        results = []
        cell_results = []
        spgr_results = []
        elincl_results = []
        txt_results = []
        txt_ex_results = []
        date_results = []
        ccdc_num_results = []
        if ccdc_num:
            ccdc_num_results = self.structures.find_by_ccdc_num(ccdc_num)
        if ccdc_num_results:
            self.display_structures_by_idlist(ccdc_num_results)
            return
        try:
            spgr = int(spgr.split()[0])
        except Exception:
            spgr = 0
        if cell:
            states['cell'] = True
            cell_results = self.search_cell_idlist(cell)
        if spgr:
            states['spgr'] = True
            spgr_results = self.structures.find_by_it_number(spgr)
        if elincl or elexcl:
            if elincl:
                states['elincl'] = True
            if elexcl:
                states['elexcl'] = True
            elincl_results = self.search_elements(elincl, elexcl, onlythese)
        if txt:
            states['txt'] = True
            txt_results = [i[0] for i in self.structures.find_by_strings(txt)]
        if txt_ex:
            states['txt_ex'] = True
            txt_ex_results = [i[0] for i in self.structures.find_by_strings(txt_ex)]
        if date1 != date2:
            states['date'] = True
            date_results = self.find_dates(date1, date2)
        rval_results = []
        if rval > 0:
            rval_results = self.structures.find_by_rvalue(rval / 100)
        ####################
        results = combine_results(cell_results, date_results, elincl_results, results, spgr_results,
                                  txt_ex_results, txt_results, rval_results, states)
        self.display_structures_by_idlist(tuple(results))

    def display_structures_by_idlist(self, idlist: Union[list, tuple]) -> None:
        """
        Displays the structures with id in results list
        """
        self.clear_fields()
        if not idlist:
            self.statusBar().showMessage('Found {} structures.'.format(0))
            return
        searchresult = self.structures.get_all_structure_names(idlist)
        self.statusBar().showMessage('Found {} structures.'.format(len(idlist)))
        self.full_list = False
        self.set_model_from_data(searchresult)
        if idlist:
            self.ui.MaintabWidget.setCurrentIndex(0)

    @pyqtSlot(name="cell_state_changed")
    def cell_state_changed(self):
        """
        Searches a cell but with diffeent loose or strict option.
        """
        self.search_cell(self.ui.searchCellLineEDit.text())

    def get_startdir_from_dialog(self):
        return QFileDialog.getExistingDirectory(self, 'Open Directory', '')

    def append_file_dirs(self, startdir: Union[str, None] = None):
        """Appends new files to database instead of creating a new database"""
        self.import_file_dirs(startdir=startdir, append=True)

    def import_file_dirs(self, startdir=None, append: bool = False):
        """
        Method to import res and cif files into the DB. "startdir" defines the directory where to start indexing.
        """
        self.tmpfile = True
        self.statusBar().showMessage('')
        if not append:
            self.close_db()
            self.start_db()
        self.progressbar(1, 0, 20)
        # self.abort_import_button.show()
        if not startdir:
            startdir = self.get_startdir_from_dialog()
        if not startdir:
            self.progress.hide()
            self.abort_import_button.hide()
            return
        lastid = self.structures.database.get_lastrowid()
        if not lastid:
            lastid = 1
        else:
            lastid += 1
        self.ui.importDirButton.setDisabled(True)
        self.ui.appendDirButton.setDisabled(True)
        self.ui.closeDatabaseButton.setDisabled(True)
        self.ui.p4pCellButton.setDisabled(True)
        self.ui.importDatabaseButton.setDisabled(True)
        self.thread = QThread()
        self.worker = Worker(searchpath=startdir, add_res_files=self.ui.add_res.isChecked(),
                             add_cif_files=self.ui.add_cif.isChecked(), lastid=lastid, structures=self.structures)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.index_files)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(lambda x: self.statusBar().showMessage(x))
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_progress)
        self.worker.number_of_files.connect(lambda x: self.set_maxfiles(x))
        self.thread.start()
        self.thread.finished.connect(lambda: self.do_work_after_indexing(startdir))
        self.statusBar().showMessage('Searching potential files...')
        self.statusBar().show()
        self.abort_import_button.clicked.connect(self.abort_indexing)

    def abort_indexing(self):
        self.worker.stop = True
        self.enable_buttons()
        self.progress.hide()
        self.statusBar().showMessage("Indexing aborted")
        self.progress.hide()
        # self.close_db()

    def set_maxfiles(self, number: int):
        self.abort_import_button.show()
        self.maxfiles = number

    def report_progress(self, progress: int):
        self.progressbar(progress, 0, self.maxfiles)

    def do_work_after_indexing(self, startdir: str):
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
        self.structures.make_indexes()
        self.structures.database.commit_db()
        self.ui.cifList_tableView.show()
        self.show_full_list()
        self.settings.save_current_dir(str(Path(startdir)))
        os.chdir(str(Path(startdir).parent))
        self.enable_buttons()
        # self.statusBar().showMessage(f'Found {self.maxfiles} files.')

    def enable_buttons(self):
        self.ui.saveDatabaseButton.setEnabled(True)
        self.ui.ExportAsCIFpushButton.setEnabled(True)
        self.ui.importDirButton.setEnabled(True)
        self.ui.appendDirButton.setEnabled(True)
        self.ui.closeDatabaseButton.setEnabled(True)
        self.ui.p4pCellButton.setEnabled(True)
        self.ui.importDatabaseButton.setEnabled(True)

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
        self.ui.appendDirButton.setDisabled(True)
        self.ui.saveDatabaseButton.setDisabled(True)
        self.ui.ExportAsCIFpushButton.setDisabled(True)
        with suppress(Exception):
            self.structures.database.commit_db()
        self.ui.searchCellLineEDit.clear()
        self.ui.txtSearchEdit.clear()
        # self.ui.cifList_tableView.clear()
        with suppress(Exception):
            self.structures.database.cur.close()
        with suppress(Exception):
            self.structures.database.con.close()
        with suppress(Exception):
            os.close(self.dbfdesc)
            self.dbfdesc = None
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
        self.ui.DatabaseNameDisplayLabel.setText('')
        self.set_model_from_data([])
        self.clear_fields()
        self.ui.MaintabWidget.setCurrentIndex(0)
        self.statusBar().showMessage('Database closed')
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
        self.ui.appendDirButton.setEnabled(True)

    @pyqtSlot(QItemSelection, QItemSelection, name="get_properties")
    def get_properties(self, selected, deselected) -> bool:
        """
        This slot shows the properties of a cif file in the properties widget
        """
        try:
            structure_id = selected.indexes()[0].data()
        except IndexError:
            return False
        self.structureId = structure_id
        dic = self.structures.get_row_as_dict(structure_id)
        self.display_properties(structure_id, dic)
        return True

    def export_current_cif(self):
        filename, _ = self.get_save_name_from_dialog(filter='*.cif')
        if not filename or not self.structureId:
            return
        cif_data = self.structures.get_cif_export_data(self.structureId)
        export_to_cif_file(cif_data, filename=filename)
        print('cif exported')

    def get_save_name_from_dialog(self, dir: str = './', filter="*.sqlite"):
        return QFileDialog.getSaveFileName(self, caption='Save File', directory=dir, filter=filter)

    def save_database(self, save_name=None) -> bool:
        """
        Saves the database to a certain file. Therefore I have to close the database.
        """
        if not hasattr(self.structures, 'database'):
            return False
        self.structures.database.commit_db()
        if self.structures.database.con.total_changes > 0:
            self.structures.set_database_version(0)
        status = False
        if not save_name:
            save_name, _ = self.get_save_name_from_dialog(dir=self.settings.load_last_workdir())
        if save_name:
            if isfile(save_name) and samefile(self.dbfilename, save_name):
                self.statusBar().showMessage("You can not save to the currently opened file!", msecs=5000)
                return False
            status = self.close_db(save_name)
            os.chdir(str(Path(save_name).parent))
            self.settings.save_current_dir(str(Path(save_name).parent))
        if status:
            self.ui.DatabaseNameDisplayLabel.setText('')
            self.statusBar().showMessage("Database saved.", msecs=5000)
            # self.open_database_file(save_name)

    def eventFilter(self, object, event):
        """Event filter for mouse clicks."""
        if event.type() == QEvent.MouseButtonDblClick:
            self.copyUnitCell()
        return False

    def keyPressEvent(self, q_key_event):
        """
        Event filter for key presses.
        Essentially searches for enter key presses in search fields and runs advanced search.
        """
        if q_key_event.key() == Qt.Key_Return or q_key_event.key() == Qt.Key_Enter:
            fields = [self.ui.adv_elementsExclLineEdit, self.ui.adv_elementsIncLineEdit, self.ui.adv_textsearch,
                      self.ui.adv_textsearch_excl, self.ui.adv_unitCellLineEdit, self.ui.adv_R1_search_line]
            for x in fields:
                if x.hasFocus():
                    self.advanced_search()
        else:
            super().keyPressEvent(q_key_event)

    def view_molecule(self) -> None:
        cell = self.structures.get_cell_by_id(self.structureId)
        if not cell:
            print('No cell found')
            return
        if self.ui.growCheckBox.isChecked():
            symmcards = [x.split(',') for x in self.structures.get_row_as_dict(self.structureId)
            ['_space_group_symop_operation_xyz'].replace("'", "").replace(" ", "").split("\n")]
            if symmcards[0] == ['']:
                print('Cif file has no symmcards, unable to grow structure.')
                self.show_asymmetric_unit()
                return
            self.ui.molGroupBox.setTitle('Completed Molecule')
            atoms = self.structures.get_atoms_table(self.structureId, cartesian=False, as_list=True)
            if atoms:
                sdm = SDM(atoms, symmcards, cell)
                needsymm = sdm.calc_sdm()
                atoms = sdm.packer(sdm, needsymm)
                self.ui.render_widget.open_molecule(atoms)
        else:
            self.show_asymmetric_unit()

    def show_asymmetric_unit(self):
        self.ui.molGroupBox.setTitle('Asymmetric Unit')
        atoms = self.structures.get_atoms_table(self.structureId, cartesian=True, as_list=False)
        if atoms:
            self.ui.render_widget.open_molecule(atoms)

    def redraw_molecule(self) -> None:
        self.view_molecule()

    def display_properties(self, structure_id, cif_dic):
        """
        Displays the residuals from the cif file
        _refine_ls_number_reflns -> unique reflect. (Independent reflections)
        _reflns_number_gt        -> unique über 2sigma (Independent reflections >2sigma)
        """
        self.clear_fields()
        cell = self.structures.get_cell_by_id(structure_id)
        if self.ui.cellSearchCSDLineEdit.isEnabled() and cell:
            self.ui.cellSearchCSDLineEdit.setText("  ".join([str(round(x, 5)) for x in cell[:6]]))
            with suppress(KeyError, TypeError):
                cstring = cif_dic['_space_group_centring_type']
                self.ui.lattCentComboBox.setCurrentIndex(centering_letter_2_num[cstring])
        if not cell:
            return False
        self.redraw_molecule()
        self.ui.cifList_tableView.setFocus()
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
        # wR2:
        with suppress(ValueError, TypeError):
            if cif_dic['_refine_ls_wR_factor_ref']:
                self.ui.wR2LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_wR_factor_ref']))
            else:
                self.ui.wR2LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_wR_factor_gt']))
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
            self.ui.flackXLineEdit.setText("{}".format(cif_dic['_refine_ls_abs_structure_Flack']))
        except KeyError:
            pass
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
            d = wavelen / (2 * sin(radians(thetamax)))
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
        try:
            if not self.structures:
                return False  # Empty database
        except Exception:
            return False  # No database cursor
        searchresult = []
        if len(search_string) == 0:
            self.show_full_list()
            return False
        if len(search_string) >= 2 and "*" not in search_string:
            search_string = "{}{}{}".format('*', search_string, '*')
        try:
            searchresult = self.structures.find_by_strings(search_string)
        except AttributeError as e:
            print(e)
        try:
            self.statusBar().showMessage("Found {} structures.".format(len(searchresult)))
            self.set_model_from_data(searchresult)
        except Exception:
            self.statusBar().showMessage("Nothing found.")

    def search_cell_idlist(self, cell: list) -> list:
        """
        Searches for a unit cell and resturns a list of found database ids.
        This method does not validate the cell. This has to be done before!
        """
        volume = misc.vol_unitcell(*cell)
        if self.ui.moreResultsCheckBox.isChecked() or self.ui.adv_moreResultscheckBox.isChecked():
            # more results:
            print('more results activated')
            atol, ltol, vol_threshold = more_results_parameters(volume)
        else:
            # regular:
            atol, ltol, vol_threshold = regular_results_parameters(volume)
        try:
            # the fist number in the result is the structureid:
            cells = self.structures.find_by_volume(volume, vol_threshold)
            print(f'{len(cells)} cells to check at {vol_threshold:.2f} threshold.')
            if self.ui.sublattCheckbox.isChecked() or self.ui.adv_superlatticeCheckBox.isChecked():
                # sub- and superlattices:
                for v in [volume * x for x in [2.0, 3.0, 4.0, 6.0, 8.0, 10.0]]:
                    # First a list of structures where the volume is similar:
                    cells.extend(self.structures.find_by_volume(v, vol_threshold))
                cells = list(set(cells))
        except (ValueError, AttributeError):
            if not self.full_list:
                self.ui.cifList_tableView.model().setData(value=[])
                self.statusBar().showMessage('Found 0 structures.')
            return []
        # Real lattice comparing in G6:
        idlist = []
        if cells:
            lattice1 = lattice.Lattice.from_parameters(*cell)
            self.statusBar().clearMessage()
            for num, curr_cell in enumerate(cells):
                self.progressbar(num, 0, len(cells) - 1)
                try:
                    lattice2 = lattice.Lattice.from_parameters(*curr_cell[1:7])
                except ValueError:
                    continue
                mapping = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
                if mapping:
                    idlist.append(curr_cell[0])
        return idlist

    @pyqtSlot('QString', name='search_cell')
    def search_cell(self, search_string: str) -> bool:
        """
        searches db for given cell via the cell volume
        """
        cell = is_valid_cell(search_string)
        self.ui.adv_unitCellLineEdit.setText('  '.join([str(x) for x in cell]))
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
            self.ui.cifList_tableView.model().resetInternalData()
            self.statusBar().showMessage('Found 0 structures.', msecs=0)
            return False
        print(f'Found {len(idlist)} results.')
        searchresult = self.structures.get_all_structure_names(idlist)
        # self.statusBar().showMessage('Found {} structures.'.format(len(idlist)))
        self.full_list = False
        self.set_model_from_data(searchresult)
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

    def get_import_filename_from_dialog(self, dir: str = './'):
        return QFileDialog.getOpenFileName(self, caption='Open File', directory=dir, filter="*.sqlite")[0]

    def get_excel_export_filename_from_dialog(self, dir: str = './'):
        return QFileDialog.getSaveFileName(self, caption='Save Excel File', directory=dir, filter="*.xlsx")[0]

    def open_database_file(self, fname=None) -> bool:
        """
        Import a new database.
        """
        self.tmpfile = False
        if not fname:
            with suppress(FileNotFoundError, OSError):
                os.chdir(self.settings.load_last_workdir())
            fname = self.get_import_filename_from_dialog(dir=self.settings.load_last_workdir())
        if not fname:
            return False
        self.close_db()
        self.clear_fields()
        self.dbfilename = fname
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
        print("Opened {}.".format(fname))
        self.settings.save_current_dir(str(Path(fname).parent))
        os.chdir(str(Path(fname).parent))
        self.ui.saveDatabaseButton.setEnabled(True)
        self.ui.appendDirButton.setEnabled(True)
        self.ui.ExportAsCIFpushButton.setEnabled(True)
        self.ui.DatabaseNameDisplayLabel.setText('Database opened: {}'.format(fname))
        self.display_number_of_structures()
        return True

    def display_number_of_structures(self):
        number = self.structures.get_largest_id()
        self.ui.statusbar.showMessage(f'Database with {number} structures loaded.')

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
        if p4p and p4p.cell:
            try:
                self.ui.searchCellLineEDit.setText('{:<6.3f} {:<6.3f} {:<6.3f} '
                                                   '{:<6.3f} {:<6.3f} {:<6.3f}'.format(*p4p.cell))
            except TypeError:
                pass
        else:
            self.moving_message('Could not read P4P file!')

    def search_for_res_cell(self, fname):
        if fname:
            shx = ShelXFile(fname)
        else:
            return
        if shx and shx.cell:
            with suppress(TypeError):
                self.ui.searchCellLineEDit.setText('{:<6.3f} {:<6.3f} {:<6.3f} '
                                                   '{:<6.3f} {:<6.3f} {:<6.3f}'.format(*shx.cell))
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
        if cif and cif.cell:
            with suppress(TypeError):
                self.ui.searchCellLineEDit.setText('{:<6.3f} {:<6.3f} {:<6.3f} '
                                                   '{:<6.3f} {:<6.3f} {:<6.3f}'.format(*cif.cell[:6]))
        else:
            self.moving_message('Could not read cif file!')

    def moving_message(self, message="", times=20):
        for s in range(times):
            time.sleep(0.05)
            self.statusBar().showMessage("{}{}".format(' ' * s, message))

    def set_columnsize(self):
        """
        TODO: currently unused
        Sets columnsize of main structure list.
        """
        self.ui.cifList_tableView.sortByColumn(1, 0)
        treewidth = self.ui.cifList_tableView.width()
        self.ui.cifList_tableView.setColumnWidth(0, int(treewidth / 4.0))
        self.ui.cifList_tableView.setColumnWidth(1, int(treewidth / 5.0))
        # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        # self.ui.cifList_treeWidget.resizeColumnToContents(1)

    def show_full_list(self) -> None:
        """
        Displays the complete list of structures
        [structure_id, meas, path, filename, data]
        """
        data = []
        try:
            if not self.structures:
                return None
        except Exception:
            return None
        if self.structures:
            data = self.structures.get_all_structure_names()
            self.set_model_from_data(data)
        # mess = "Loaded {} entries.".format(len(data))
        # self.statusBar().showMessage(mess, msecs=5000)
        self.full_list = True
        self.ui.SpGrpComboBox.setCurrentIndex(0)
        self.ui.adv_elementsIncLineEdit.clear()
        self.ui.adv_elementsExclLineEdit.clear()
        self.ui.adv_moreResultscheckBox.setChecked(False)
        self.ui.adv_superlatticeCheckBox.setChecked(False)
        self.ui.adv_textsearch.clear()
        self.ui.adv_textsearch_excl.clear()
        self.ui.adv_unitCellLineEdit.clear()
        self.ui.CCDCNumLineEdit.clear()
        # I need this to reset the date after clearing the search values in advanced search:
        self.ui.dateEdit1.setDate(QDate(date.today()))
        self.ui.dateEdit2.setDate(QDate(date.today()))
        self.ui.MaintabWidget.setCurrentIndex(0)

    def clear_fields(self) -> None:
        """
        Clears all residuals fields.
        """
        self.ui.allCifTreeWidget.clear()
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
        self.ui.cellField.clear()
        self.ui.render_widget.clear()
        self.table_model.clear()


if __name__ == "__main__":
    def my_exception_hook(exctype, value, error_traceback):
        """
        Hooks into Exceptions to create debug reports.
        """
        errortext = 'StructureFinder V{} crash report\n\n'.format(VERSION)
        errortext += 'Please send also the corresponding CIF file, if possible.'
        errortext += 'Python ' + sys.version + '\n'
        errortext += sys.platform + '\n'
        errortext += time.asctime(time.localtime(time.time())) + '\n'
        errortext += "StructureFinder crashed during the following operation:" + '\n'
        errortext += '-' * 80 + '\n'
        errortext += ''.join(traceback.format_tb(error_traceback)) + '\n'
        errortext += str(exctype.__name__) + ': '
        errortext += str(value) + '\n'
        errortext += '-' * 80 + '\n'
        logfile = Path.home().joinpath(Path(r'StructureFinder-crash.txt'))
        try:
            logfile.write_text(errortext)
        except PermissionError:
            pass
        sys.__excepthook__(exctype, value, error_traceback)
        # Hier Fenster für meldung öffnen
        bug_found_warning(logfile)
        sys.exit(1)


    if not DEBUG:
        sys.excepthook = my_exception_hook

    app.setWindowIcon(QtGui.QIcon('../icons/strf.png'))
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