#!/usr/bin/python3
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

os.environ['QT_API'] = 'PyQt6'
import shutil
import sys
import tempfile
import time
import traceback
from contextlib import suppress
from datetime import date
from math import radians, sin
from os.path import isfile, samefile
from pathlib import Path
from sqlite3 import DatabaseError, ProgrammingError
from xml.etree.ElementTree import ParseError

import gemmi

from structurefinder.plot.plot_widget import PlotWidget

if hasattr(gemmi, 'set_leak_warnings'):
    gemmi.set_leak_warnings(False)
import gemmi.cif
import qtawesome as qta
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import QDate, QEvent, QItemSelection, QModelIndex, QPoint, Qt, QThread
from qtpy.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QProgressBar, QPushButton, \
    QTreeWidgetItem
from shelxfile import Shelxfile

from structurefinder import strf_cmd
from structurefinder.ccdc.query import parse_results, search_csd
from structurefinder.displaymol.sdm import SDM
from structurefinder.gui.strf_main import Ui_stdbMainwindow
from structurefinder.gui.table_model import CustomProxyModel, TableModel
from structurefinder.misc.dialogs import bug_found_warning, do_update_program
from structurefinder.misc.download import MyDownloader
from structurefinder.misc.exporter import export_to_cif_file
from structurefinder.misc.settings import StructureFinderSettings
from structurefinder.misc.version import VERSION
from structurefinder.p4pfile.p4p_reader import P4PFile, read_file_to_list
from structurefinder.pymatgen.core import lattice
from structurefinder.searcher import constants, database_handler, misc
from structurefinder.searcher.cif_file import CifFile
from structurefinder.searcher.constants import (
    centering_letter_2_num,
    centering_num_2_letter,
)
from structurefinder.searcher.database_handler import columns
from structurefinder.searcher.misc import (
    combine_results,
    elements,
    is_valid_cell,
    more_results_parameters,
    regular_results_parameters,
)
from structurefinder.searcher.search_worker import SearchWorker

DEBUG = False

# This is to make sure that strf finds the application path even when it is
# executed from another path e.g. when opened via "open file" in windows:
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
else:
    application_path = Path(os.path.abspath(__file__)).parent.parent

app = QApplication(sys.argv)
if sys.platform == "win32":
    app.setStyle("windowsvista")
print(sys.version)


class StartStructureDB(QMainWindow):
    def __init__(self, db_file_name: str = '', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread = None
        self.worker = None
        self.settings = StructureFinderSettings()
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        self.set_window_size_and_position()
        font = QtGui.QFont()
        font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
        self.ui.SHELXplainTextEdit.setFont(font)
        self.statusbar: QtWidgets.QStatusBar = self.statusBar()
        self.upd = None
        self.maxfiles = 0
        self.dbfdesc = None
        self.dbfilename = db_file_name
        self.tmpfile = False  # indicates wether a tmpfile or any other db file is used
        self.abort_import_button = QPushButton('Abort Indexing')
        self.progress = QProgressBar(self)
        # self.progress.setFixedWidth(150)
        self.statusbar.addPermanentWidget(self.progress)
        self.ui.appendDirButton.setDisabled(True)
        self.statusbar.addPermanentWidget(self.abort_import_button)
        self.abort_import_button.hide()
        self.statusbar.hide()
        self.structures: database_handler.StructureTable | None = None
        self.apx = None
        self.structureId = 0
        self.passwd = ''
        self.set_icons()
        self.show()
        self.setAcceptDrops(True)
        self.full_list = True  # indicator if the full structures list is shown
        self.ui.cellcheckExeLineEdit.setText(self.settings.load_ccdc_exe_path())
        self.connect_signals_and_slots()
        self.set_initial_button_states()
        self.ui.dateEdit1.setDate(QDate(date.today()))
        self.ui.dateEdit2.setDate(QDate(date.today()))
        self.ui.MaintabWidget.setCurrentIndex(0)
        self.statusbar.showMessage(f'StructureFinder version {VERSION}')
        # Actions for certain gui elements:
        self.ui.cellField.addAction(self.ui.actionCopy_Unit_Cell)
        # self.ui.cifList_tableView.addAction(self.ui.actionGo_to_All_CIF_Tab)
        if db_file_name:
            self.open_database_file(db_file_name)
        if self.structures:
            self.set_model_from_data(self.structures.get_structure_rows_by_ids())
        self.ui.SumformLabel.setMinimumWidth(self.ui.reflTotalLineEdit.width())
        if "PYTEST_CURRENT_TEST" not in os.environ:
            self.checkfor_version()
            self.checkfor_version()
        self.plot = PlotWidget(self)
        self.plot.point_clicked.connect(self.gotto_structure_id)
        self.ui.plot_area_verticalLayout.addWidget(self.plot)
        self.init_plot_comboboxes()

    def set_initial_button_states(self):
        self.ui.appendDatabasePushButton.setDisabled(True)
        self.ui.saveDatabaseButton.setDisabled(True)

    def set_icons(self):
        with suppress(Exception):
            self.ui.importDatabaseButton.setIcon(qta.icon('fa5s.database'))
            self.ui.saveDatabaseButton.setIcon(qta.icon('fa5.hdd'))
            self.ui.importDirButton.setIcon(qta.icon('fa5s.download'))
            self.ui.appendDirButton.setIcon(qta.icon('fa5s.plus'))
            self.ui.p4pCellButton.setIcon(qta.icon('mdi.cube-outline'))
            self.ui.closeDatabaseButton.setIcon(qta.icon('fa5.times-circle'))
            self.ui.appendDatabasePushButton.setIcon(qta.icon('fa5s.plus'))

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
        self.abort_import_button.clicked.connect(self.abort_import)
        self.ui.moreResultsCheckBox.stateChanged.connect(self.cell_state_changed)
        self.ui.sublattCheckbox.stateChanged.connect(self.cell_state_changed)
        self.ui.adv_SearchPushButton.clicked.connect(self.advanced_search)
        self.ui.adv_ClearSearchButton.clicked.connect(self.show_full_list)
        self.ui.CSDpushButton.clicked.connect(self.search_csd_and_display_results)
        # Actions:
        self.ui.actionClose_Database.triggered.connect(self.close_db)
        self.ui.actionImport_directory.triggered.connect(self.import_file_dirs)
        self.ui.actionImport_file.triggered.connect(self.open_database_file)
        self.ui.actionSave_Database.triggered.connect(self.save_database)
        self.ui.actionCopy_Unit_Cell.triggered.connect(self.copyUnitCell)
        self.ui.cifList_tableView.save_excel_triggered.connect(self.on_save_as_excel)
        self.ui.cifList_tableView.open_save_path.connect(self.on_browse_path_from_row)
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
        self.ui.cellcheckExeLineEdit.textChanged.connect(self.save_cellcheck_exe_path)
        self.ui.cellcheckExePushButton.clicked.connect(self.browse_for_ccdc_exe)
        self.ui.appendDatabasePushButton.clicked.connect(self.append_database)
        self.ui.labelsCheckBox.toggled.connect(self.show_labels)
        self.ui.helpPushButton.clicked.connect(self.show_help)
        self.ui.hideInArchivesCB.clicked.connect(self.recount)
        # Column menu:
        self.ui.cifList_tableView.header_menu.columns_changed.connect(self.show_full_list)
        self.ui.cifList_tableView.header_menu.columns_changed.connect(self.save_headers)
        # plot
        self.ui.x_axis_plot_comboBox.currentIndexChanged.connect(self.plot_data)
        self.ui.y_axis_plot_comboBox.currentIndexChanged.connect(self.plot_data)
        self.ui.dotsRadioButton.clicked.connect(self.plot_data)
        self.ui.HistogramRadioButton.clicked.connect(self.plot_data)
        self.ui.ddradioButton.hide()
        self.ui.HistogramRadioButton.hide()
        self.ui.z_axis_plot_comboBox.hide()
        self.ui.ddradioButton.clicked.connect(self.plot_data)
        self.ui.dotsRadioButton.clicked.connect(lambda: self.ui.ddradioButton.setChecked(False))
        self.ui.dotsRadioButton.clicked.connect(lambda: self.ui.HistogramRadioButton.setChecked(False))
        self.ui.ddradioButton.clicked.connect(lambda: self.ui.dotsRadioButton.setChecked(False))
        self.ui.ddradioButton.clicked.connect(lambda: self.ui.HistogramRadioButton.setChecked(False))
        self.ui.HistogramRadioButton.clicked.connect(lambda: self.ui.ddradioButton.setChecked(False))
        self.ui.HistogramRadioButton.clicked.connect(lambda: self.ui.dotsRadioButton.setChecked(False))
        # shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+G"), self)
        # shortcut.activated.connect(lambda: self.gotto_structure_id(300))

    def init_plot_comboboxes(self):
        residuals = list(database_handler.residuals)
        residuals.remove('_shelx_res_file')
        self.ui.x_axis_plot_comboBox.blockSignals(True)
        self.ui.y_axis_plot_comboBox.blockSignals(True)
        self.ui.x_axis_plot_comboBox.addItems(residuals)
        self.ui.y_axis_plot_comboBox.addItems(residuals)
        self.ui.x_axis_plot_comboBox.blockSignals(False)
        self.ui.y_axis_plot_comboBox.blockSignals(False)

    def plot_data(self):
        if not self.structures:
            return
        x_label = self.ui.x_axis_plot_comboBox.currentText()
        y_label = self.ui.y_axis_plot_comboBox.currentText()
        results = self.structures.get_plot_values(x_axis=x_label, y_axis=y_label)
        if self.ui.dotsRadioButton.isChecked():
            print('plotting points')
            self.plot.plot_points(results, x_title=x_label, y_title=y_label)
        elif self.ui.HistogramRadioButton.isChecked():
            print('plotting histogram')
            self.plot.plot_histogram_text(results, x_title=x_label, y_title=y_label)
        elif self.ui.ddradioButton.isChecked():
            print('plotting 3D')
            pass

    def save_headers(self):
        self.settings.save_visible_headers(columns.visible_headers())
        # TDDO: Doesn't work:
        # self.settings.save_column_state(self.ui.cifList_tableView.horizontalHeader().saveState())

    def load_headers(self):
        headers = self.settings.load_visible_headers()
        if headers and isinstance(headers, list):
            columns.set_visible_headers(headers)
        # TDDO: Doesn't work:
        """
        column_order = self.settings.load_column_state()
        if column_order:
            ok = self.ui.cifList_tableView.horizontalHeader().restoreState(column_order)
            print(f'state restored {ok}')"""

    def set_model_from_data(self, data: list | tuple):
        table_model = TableModel(parent=self, structures=data)
        proxy_model = CustomProxyModel(self)
        proxy_model.setSourceModel(table_model)
        self.ui.cifList_tableView.setModel(proxy_model)
        self.ui.hideInArchivesCB.toggled.connect(proxy_model.setFilterEnabled)
        proxy_model.setFilterEnabled(self.ui.hideInArchivesCB.isChecked())
        self.table_model = proxy_model
        # self.ui.cifList_tableView.setModel(self.table_model)
        self.ui.cifList_tableView.hideColumn(0)
        self.ui.cifList_tableView.selectionModel().selectionChanged.connect(self.get_properties)
        self.ui.cifList_tableView.resizeColumnToContents(3)

    def gotto_structure_id(self, value: int):
        table = self.ui.cifList_tableView
        model = table.model()
        vheader = table.verticalHeader()
        for row in range(model.rowCount()):
            header_value = vheader.model().headerData(row, QtCore.Qt.Orientation.Vertical)
            if int(header_value) == int(value):
                idx = model.index(row, 0)
                table.scrollTo(idx)
                table.selectRow(row)
                return

    def recount(self):
        if hasattr(self, 'table_model'):
            self.statusBar().showMessage(f"Database with {self.table_model.rowCount()} structures loaded", msecs=0)

    def show_help(self) -> None:
        from qtpy import QtCore
        from qtpy.QtGui import QDesktopServices
        QDesktopServices.openUrl(QtCore.QUrl('https://dkratzert.de/files/structurefinder/docs/'))

    def show_labels(self, value: bool):
        self.ui.render_widget.show_labels(value)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._savesize()

    def moveEvent(self, event: QtGui.QMoveEvent) -> None:
        """Is called when the main window moves."""
        super().moveEvent(event)
        self._savesize()

    def changeEvent(self, event: QtCore.QEvent) -> None:
        """Is called when the main window changes its state."""
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            self._savesize()

    def close(self):
        self.save_headers()

    def closeEvent(self, event):
        self.save_headers()
        super().closeEvent(event)

    def _savesize(self) -> None:
        """Saves the main window size nd position."""
        x, y = self.pos().x(), self.pos().y()
        self.settings.save_window_position(QPoint(x, y), self.size(), self.isMaximized())

    def set_window_size_and_position(self) -> None:
        wsettings = self.settings.load_window_position()
        self.resize(wsettings.size)
        self.move(wsettings.position)
        if wsettings.maximized:
            self.showMaximized()

    def checkfor_version(self):
        url = 'https://dkratzert.de/files/structurefinder/version.txt'
        self.upd = MyDownloader(parent=self, url=url)
        self.upd.finished.connect(self.show_update_warning)
        self.upd.failed.connect(self.upd.failed_to_download)
        self.upd.progress.connect(self.upd.print_status)
        self.upd.start()

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
            print(f'Version {remote_version} is outdated (actual is {VERSION}).')
            warn_text = "A newer version of StructureFinder is available under " \
                        "<a href='https://dkratzert.de/structurefinder.html'>" \
                        "https://dkratzert.de/structurefinder.html</a>"
            box = QMessageBox()
            box.setTextFormat(Qt.TextFormat.AutoText)
            box.setWindowTitle(" ")
            box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            if sys.platform.startswith("win"):
                warn_text += r"<br><br>Updating now will end all running StructureFinder programs!"
                update_button = box.addButton('Update Now', QMessageBox.ButtonRole.AcceptRole)
                update_button.clicked.connect(lambda: do_update_program(str(remote_version)))
            box.setText(warn_text.format(remote_version))
            box.exec()
        else:
            print(f'Remote version {remote_version} is up to date.')

    def save_cellcheck_exe_path(self, text: str):
        self.settings.save_ccdc_exe_path(text)

    def browse_for_ccdc_exe(self):
        exe = QFileDialog.getOpenFileName(self, caption='CellCheckCSD executable',
                                          filter="ccdc_searcher.bat;ccdc_searcher")[0]
        if exe:
            self.ui.cellcheckExeLineEdit.setText(exe)

    def append_database(self) -> None:
        file_name = self.get_import_filename_from_dialog()
        if not file_name or not Path(file_name).is_file():
            return
        if Path(file_name).samefile(self.structures.dbfilename):
            QMessageBox.information(self, 'This is the same file', 'Can not merge same files.')
            return
        try:
            tst = database_handler.StructureTable(file_name)
            if len(tst) < 1:
                print('New database has no entries, aborting.')
                return None
            del tst
        except Exception as e:
            print(f'Unable to append database: {e}')
            self.ui.statusbar.showMessage('Unable to merge databases.')
            return
        self.structures.database.merge_databases(file_name)
        dbfile = self.structures.dbfilename
        self.close_db()
        self.open_database_file(dbfile)
        self.ui.statusbar.showMessage(f'Merging databases finished. '
                                      f'New database has {len(self.structures)} structures now.')

    def res_checkbox_clicked(self, click):
        if not any([self.ui.add_res.isChecked(), self.ui.add_cif.isChecked()]):
            self.ui.add_res.setChecked(True)

    def cif_checkbox_clicked(self, click):
        if not any([self.ui.add_res.isChecked(), self.ui.add_cif.isChecked()]):
            self.ui.add_cif.setChecked(True)

    def on_save_as_excel(self):
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
        for col, name in enumerate(columns.visible_header_names()):
            worksheet.write(0, col, name)
        for row, index in enumerate(selection):
            for column in range(self.ui.cifList_tableView.model().columnCount()):
                cell_data = self.ui.cifList_tableView.get_field_content(index.row(), column)
                worksheet.write(row + 1, column, cell_data)
        workbook.close()

    def on_browse_path_from_row(self, curdir: str):
        import subprocess
        curdir = Path(curdir).resolve()
        if sys.platform == "win" or sys.platform == "win32":
            subprocess.Popen(['explorer', str(curdir)], shell=True)
        if sys.platform == 'darwin':
            subprocess.call(['open', str(curdir)])
        if sys.platform == 'linux':
            subprocess.call(['xdg-open', str(curdir)])

    def show_csdentry(self, item: QModelIndex):
        import webbrowser
        sel = self.ui.CSDtreeWidget.selectionModel().selection()
        try:
            identifier = sel.indexes()[8].data()
        except KeyError:
            return None
        webbrowser.open_new_tab(f'https://www.ccdc.cam.ac.uk/structures/Search?entry_list={identifier}')

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
        xml = search_csd(cell, centering=center, searcher_executable=self.ui.cellcheckExeLineEdit.text())
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
            self.ui.statusbar.showMessage(f'Copied unit cell {cell} to clip board.')
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
            txt_results = self.structures.find_text_and_authors(txt)
        if txt_ex:
            states['txt_ex'] = True
            txt_ex_results = self.structures.find_text_and_authors(txt_ex)
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

    def display_structures_by_idlist(self, idlist: list | tuple) -> None:
        """
        Displays the structures with id in results list
        """
        self.clear_fields()
        if not idlist:
            self.statusBar().showMessage(f'Found {0} structures.')
            return
        searchresult = self.structures.get_structure_rows_by_ids(idlist)
        self.full_list = False
        self.set_model_from_data(searchresult)
        self.statusBar().showMessage(f'Found {self.table_model.rowCount()} structures.')
        if idlist:
            self.ui.MaintabWidget.setCurrentIndex(0)

    def cell_state_changed(self):
        """
        Searches a cell but with diffeent loose or strict option.
        """
        self.search_cell(self.ui.searchCellLineEDit.text())

    def get_startdir_from_dialog(self):
        return QFileDialog.getExistingDirectory(self, 'Open Directory', directory=self.settings.load_last_indexdir())

    def append_file_dirs(self, startdir: str | None = None):
        """Appends new files to database instead of creating a new database"""
        self.import_file_dirs(startdir=startdir, append=True)

    def import_file_dirs(self, startdir=None, append: bool = False):
        """
        Method to import res and cif files into the DB. "startdir" defines the directory where to start indexing.
        """
        self.tmpfile = True
        self.statusBar().showMessage('')
        if not startdir:
            startdir = self.get_startdir_from_dialog()
        if not startdir:
            self.progress.hide()
            self.abort_import_button.hide()
            return
        if not append:
            self.close_db()
            self.start_db()
        self.progressbar(1, 0, 20)
        self.abort_import_button.show()
        self.ui.importDirButton.setDisabled(True)
        self.ui.appendDirButton.setDisabled(True)
        self.ui.closeDatabaseButton.setDisabled(True)
        self.ui.p4pCellButton.setDisabled(True)
        self.ui.appendDatabasePushButton.setDisabled(True)
        self.ui.importDatabaseButton.setDisabled(True)
        self.thread = QThread(self)
        self.worker = SearchWorker(self, startdir, self.structures,
                                   add_res=self.ui.add_res.isChecked(),
                                   add_cif=self.ui.add_cif.isChecked(),
                                   no_archives=self.ui.ignoreArchivesCB.isChecked())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.progress.hide)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.abort_import_button.hide)
        self.worker.progress.connect(self.report_progress)
        self.worker.number_of_files.connect(lambda x: self.set_maxfiles(x))
        self.thread.start()
        self.worker.finished.connect(lambda: self.do_work_after_indexing(startdir))
        self.statusBar().showMessage('Searching potential files...')
        self.statusBar().show()
        self.abort_import_button.clicked.connect(self.abort_indexing)

    def abort_indexing(self):
        self.worker.stop = True
        self.enable_buttons()
        self.abort_import_button.hide()
        self.progress.hide()
        self.statusBar().showMessage("Indexing aborted")
        self.progress.hide()
        # self.close_db()

    def set_maxfiles(self, number: int):
        self.abort_import_button.show()
        self.maxfiles = number

    def report_progress(self, progress: int):
        self.statusbar.showMessage(f'Inspected {progress} files')
        self.progressbar(progress, 0, self.maxfiles)
        if progress % 10 == 0:
            app.processEvents()

    def do_work_after_indexing(self, startdir: str):
        self.progress.hide()
        strf_cmd.finish_database(self.structures)
        self.ui.cifList_tableView.show()
        self.show_full_list()
        self.settings.save_current_index_dir(str(Path(startdir)))
        self.enable_buttons()

    def enable_buttons(self):
        self.ui.appendDatabasePushButton.setEnabled(True)
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

    def close_db(self, copy_on_close: str = None) -> bool:
        """
        Closed the current database and erases the list.
        copy_on_close is used to save the databse into a file during close_db().
        :param copy_on_close: Path to where the file should be copied after close()
        """
        self.ui.appendDirButton.setDisabled(True)
        self.ui.appendDatabasePushButton.setDisabled(True)
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
            if self.tmpfile and not self.remove_db_tempfile():
                return False
        self.ui.DatabaseNameDisplayLabel.setText('')
        self.set_model_from_data([])
        self.clear_fields()
        self.ui.MaintabWidget.setCurrentIndex(0)
        self.statusBar().showMessage('Database closed')
        return True

    def remove_db_tempfile(self) -> bool:
        try:
            os.remove(self.dbfilename)
            self.dbfilename = ''
        except Exception:
            return False
        return True

    def abort_import(self):
        """
        This slot means, import was aborted.
        """
        self.worker.stop()

    def start_db(self):
        """
        Initializes the database.
        """
        self.dbfdesc, self.dbfilename = tempfile.mkstemp()
        self.structures = database_handler.StructureTable(self.dbfilename)
        self.structures.database.initialize_db()
        self.ui.appendDirButton.setEnabled(True)

    def get_properties(self, selected: QItemSelection, _: QItemSelection) -> bool:
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

    def get_save_name_from_dialog(self, directory: str = '', filter="*.sqlite"):
        if not directory:
            directory = self.settings.load_last_workdir()
        return QFileDialog.getSaveFileName(self, caption='Save File', directory=directory, filter=filter)

    def save_database(self, save_name=None) -> bool:
        """
        Saves the database to a certain file. Therefore I have to close the database.
        """
        if not hasattr(self.structures, 'database'):
            return False
        self.structures.database.commit_db()
        # if self.structures.database.con.total_changes > 0:
        #    self.structures.set_database_version(0)
        status = False
        if not save_name:
            save_name, _ = self.get_save_name_from_dialog()
        if save_name:
            if isfile(save_name) and samefile(self.dbfilename, save_name):
                self.statusBar().showMessage("You can not save to the currently opened file!", msecs=5000)
                return False
            status = self.close_db(save_name)
            self.settings.save_current_work_dir(str(Path(save_name).resolve().parent))
        if status:
            self.ui.DatabaseNameDisplayLabel.setText('')
            self.statusBar().showMessage("Database saved.", msecs=5000)
            self.open_database_file(save_name)

    def eventFilter(self, object, event):
        """Event filter for mouse clicks."""
        if event.type() == QEvent.Type.MouseButtonDblClick:
            self.copyUnitCell()
        return False

    def keyPressEvent(self, q_key_event):
        """
        Event filter for key presses.
        Essentially searches for enter key presses in search fields and runs advanced search.
        """
        if q_key_event.key() == Qt.Key.Key_Return or q_key_event.key() == Qt.Key.Key_Enter:
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
                self.ui.render_widget.open_molecule(atoms, labels=self.ui.labelsCheckBox.isChecked())
        else:
            self.show_asymmetric_unit()

    def show_asymmetric_unit(self):
        self.ui.molGroupBox.setTitle('Asymmetric Unit')
        atoms = self.structures.get_atoms_table(self.structureId, cartesian=True, as_list=False)
        if atoms:
            self.ui.render_widget.open_molecule(atoms, labels=self.ui.labelsCheckBox.isChecked())

    def redraw_molecule(self) -> None:
        self.view_molecule()

    def display_properties(self, structure_id, cif_dic: CifFile):
        """
        Displays the residuals from the cif file
        _refine_ls_number_reflns -> unique reflect. (Independent reflections)
        _reflns_number_gt        -> unique über 2sigma (Independent reflections >2sigma)
        """
        self.clear_fields()
        cell = self.structures.get_cell_by_id(structure_id)
        if self.ui.cellSearchCSDLineEdit.isEnabled() and cell:
            with suppress(TypeError):
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
                self.ui.wR2LineEdit.setText(f"{cif_dic['_refine_ls_wR_factor_ref']:>5.4f}")
            else:
                self.ui.wR2LineEdit.setText(f"{cif_dic['_refine_ls_wR_factor_gt']:>5.4f}")
        try:  # R1:
            if cif_dic['_refine_ls_R_factor_gt']:
                self.ui.r1LineEdit.setText(f"{cif_dic['_refine_ls_R_factor_gt']:>5.4f}")
            else:
                self.ui.r1LineEdit.setText(f"{cif_dic['_refine_ls_R_factor_all']:>5.4f}")
        except (ValueError, TypeError):
            pass
        self.ui.zLineEdit.setText(f"{cif_dic['_cell_formula_units_Z']}")
        try:
            sumform = misc.format_sum_formula(self.structures.get_calc_sum_formula(structure_id))
        except KeyError:
            sumform = ''
        if sumform == '':
            # Display this as last resort:
            sumform = cif_dic['_chemical_formula_sum']
        self.ui.SumformLabel.setMinimumWidth(self.ui.reflTotalLineEdit.width())
        self.ui.SumformLabel.setText(f"{sumform}")
        self.ui.reflTotalLineEdit.setText(f"{cif_dic['_diffrn_reflns_number']}")
        self.ui.uniqReflLineEdit.setText(f"{cif_dic['_refine_ls_number_reflns']}")
        self.ui.refl2sigmaLineEdit.setText(f"{cif_dic['_reflns_number_gt']}")
        self.ui.goofLineEdit.setText(f"{cif_dic['_refine_ls_goodness_of_fit_ref']}")
        it_num = cif_dic['_space_group_IT_number']
        if it_num:
            it_num = f"({it_num})"
        self.ui.SpaceGroupLineEdit.setText(f"{cif_dic['_space_group_name_H_M_alt']} {it_num}")
        self.ui.temperatureLineEdit.setText(f"{cif_dic['_diffrn_ambient_temperature']}")
        self.ui.maxShiftLineEdit.setText(f"{cif_dic['_refine_ls_shift_su_max']}")
        peak = cif_dic['_refine_diff_density_max']
        if peak:
            self.ui.peakLineEdit.setText(f"{peak} / {cif_dic['_refine_diff_density_min']}")
        self.ui.rintLineEdit.setText(f"{cif_dic['_diffrn_reflns_av_R_equivalents']}")
        self.ui.rsigmaLineEdit.setText(f"{cif_dic['_diffrn_reflns_av_unetI_netI']}")
        self.ui.cCDCNumberLineEdit.setText(f"{cif_dic['_database_code_depnum_ccdc_archive']}")
        try:
            self.ui.flackXLineEdit.setText(f"{cif_dic['_refine_ls_abs_structure_Flack']}")
        except KeyError:
            pass
        try:
            dat_param = int(cif_dic['_refine_ls_number_reflns']) / int(cif_dic['_refine_ls_number_parameters'])
        except (ValueError, ZeroDivisionError, TypeError):
            dat_param = 0.0
        self.ui.dataReflnsLineEdit.setText(f"{dat_param:<5.1f}")
        self.ui.numParametersLineEdit.setText(f"{cif_dic['_refine_ls_number_parameters']}")
        thetamax = cif_dic['_diffrn_reflns_theta_max']
        # d = lambda/2sin(theta):
        try:
            wavelen = float(cif_dic['_diffrn_radiation_wavelength'])
            d = wavelen / (2 * sin(radians(thetamax)))
        except(ZeroDivisionError, TypeError, ValueError):
            d = 0.0
            wavelen = 0.0
        self.ui.numRestraintsLineEdit.setText(f"{cif_dic['_refine_ls_number_restraints']}")
        self.ui.thetaMaxLineEdit.setText(f"{thetamax}")
        self.ui.thetaFullLineEdit.setText(f"{cif_dic['_diffrn_reflns_theta_full']}")
        self.ui.dLineEdit.setText(f"{d:5.3f}")
        self.ui.lastModifiedLineEdit.setText(cif_dic['modification_time'])
        try:
            compl = cif_dic['_diffrn_measured_fraction_theta_max'] * 100
            if not compl:
                compl = 0.0
        except TypeError:
            compl = 0.0
        try:
            self.ui.completeLineEdit.setText(f"{compl:<5.1f}")
        except ValueError:
            pass
        self.ui.wavelengthLineEdit.setText(f"{wavelen}")
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

    def find_dates(self, date1: str, date2: str) -> list[int]:
        """
        Returns a list if id between date1 and date2
        """
        if not date1:
            date1 = '0000-01-01'
        if not date2:
            date2 = 'NOW'
        result = self.structures.find_by_date(date1, date2)
        return result

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
            search_string = f"{'*'}{search_string}{'*'}"
        try:
            searchresult = self.structures.find_text_and_authors(search_string)
        except AttributeError as e:
            print(e)
        if searchresult:
            self.set_model_from_data(self.structures.get_structure_rows_by_ids(searchresult))
        else:
            self.set_model_from_data([])
        self.statusBar().showMessage(f"Found {self.table_model.rowCount()} structures.")
        return True

    def search_cell_idlist(self, cell: list) -> list:
        """
        Searches for a unit cell and resturns a list of found database ids.
        This method does not validate the cell. This has to be done before!
        """
        try:
            volume = misc.vol_unitcell(*cell)
            if volume < 0.01:
                return []
        except ValueError:
            return []
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
        self.progress.hide()
        self.statusBar().showMessage(f'Found {len(idlist)} structures.')
        return idlist

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
            self.set_model_from_data([])
            return False
        searchresult = self.structures.get_structure_rows_by_ids(idlist)
        self.full_list = False
        self.set_model_from_data(searchresult)
        print(f'Found {self.table_model.rowCount()} results.')
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

    def get_import_filename_from_dialog(self, directory: str = ''):
        if not directory:
            directory = self.settings.load_last_workdir()
        return QFileDialog.getOpenFileName(self, caption='Open File', directory=directory, filter="*.sqlite; *.sql")[0]

    def get_excel_export_filename_from_dialog(self, directory: str = ''):
        if not directory:
            directory = self.settings.load_last_workdir()
        return QFileDialog.getSaveFileName(self, caption='Save Excel File', directory=directory, filter="*.xlsx")[0]

    def open_database_file(self, file_name=None) -> bool:
        """
        Import a new database.
        """
        self.tmpfile = False
        if not file_name:
            file_name = self.get_import_filename_from_dialog()
        if not file_name:
            return False
        self.close_db()
        self.clear_fields()
        self.dbfilename = file_name
        self.structures = database_handler.StructureTable(self.dbfilename)
        self.load_headers()
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
        print(f"Opened {file_name}.")
        self.settings.save_current_work_dir(str(Path(file_name).resolve().parent))
        self.ui.saveDatabaseButton.setEnabled(True)
        self.ui.appendDirButton.setEnabled(True)
        self.ui.ExportAsCIFpushButton.setEnabled(True)
        self.ui.DatabaseNameDisplayLabel.setText(f'Database opened: {Path(file_name).resolve()!s}')
        self.display_number_of_structures()
        self.ui.appendDatabasePushButton.setEnabled(True)
        return True

    def display_number_of_structures(self):
        # number = self.structures.get_largest_id()
        self.ui.statusbar.showMessage(f'Database with {self.table_model.rowCount()} structures loaded.')

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
            shx = Shelxfile()
            shx.read_file(fname)
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
            doc = gemmi.cif.Document()
            doc.source = fname
            try:
                doc.parse_file(fname)
            except ValueError:
                return
            cif = CifFile()
            try:
                cif.parsefile(doc)
            except FileNotFoundError:
                self.moving_message('File not found.')
        else:
            return
        if cif and cif.cell:
            with suppress(TypeError):
                self.ui.searchCellLineEDit.setText(
                    f'{cif.cell.a:<6.3f} {cif.cell.b:<6.3f} {cif.cell.c:<6.3f} '
                    f'{cif.cell.alpha:<6.3f} {cif.cell.beta:<6.3f} {cif.cell.gamma:<6.3f}')
        else:
            self.moving_message('Could not read cif file!')

    def moving_message(self, message="", times=20):
        for s in range(times):
            time.sleep(0.05)
            self.statusBar().showMessage("{}{}".format(' ' * s, message))

    def show_full_list(self) -> None:
        """
        Displays the complete list of structures
        [structure_id, meas, path, filename, data]
        """
        try:
            if not self.structures:
                return None
        except Exception:
            return None
        self.ui.cifList_tableView.header_menu.reset_sorting()
        if self.structures:
            data = self.structures.get_structure_rows_by_ids()
            self.set_model_from_data(data)
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
        self.statusBar().showMessage(f'Found {self.table_model.rowCount()} structures.', msecs=0)
        self.ui.cifList_tableView.resizeColumnToContents(columns.path.position)

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
        # self.table_model.clear()


def my_exception_hook(exctype: type[BaseException], value: BaseException, error_traceback: traceback,
                      exit=True) -> None:
    """
    Hooks into Exceptions to create debug reports.
    """
    errortext = (f'StructureFinder V{VERSION} crash report\n\n'
                 f'Please send also the corresponding CIF/RES file, if possible. \n'
                 f'Python {sys.version}\n'
                 f'Platform: {sys.platform}\n'
                 f'Date: {time.asctime(time.localtime(time.time()))}\n'
                 f'StructureFinder crashed during the following operation:\n\n'
                 f'{"-" * 120}\n'
                 # f'{"".join(traceback.format_tb(error_traceback))}\n'
                 # f'{str(exctype.__name__)}: '
                 # f'{str(value)} \n'
                 # f'{"-" * 120}\n'
                 )

    # Walk through the traceback and extract local variables
    for frame, _ in traceback.walk_tb(error_traceback):
        errortext += (f'File "{frame.f_code.co_filename}", line {frame.f_lineno}, in '
                      f'{frame.f_code.co_qualname}(...):\n')
        newline = '\n'
        errortext += '  Locals: \n    '
        errortext += "    ".join(
            [f"  {k}:{newline}          {'          '.join([x + newline for x in repr(v).splitlines()])}" for k, v in
             frame.f_locals.items()]) + '\n\n'

    errortext += f'{"-" * 120}\n'
    errortext += f'{exctype.__name__!s}: {value!s} \n'
    errortext += f'{"-" * 120}\n'

    logfile = Path.home().joinpath(Path(r'StructureFinder-crash.txt'))
    try:
        logfile.write_text(errortext)
    except PermissionError:
        pass
    sys.__excepthook__(exctype, value, error_traceback)
    bug_found_warning(logfile)
    if exit:
        sys.exit(1)


def main():
    if not DEBUG:
        sys.excepthook = my_exception_hook
    app.setWindowIcon(QtGui.QIcon(str(Path(application_path, 'icons/strf.png').resolve())))
    # Has to be without version number, because QWebengine stores data in ApplicationName directory:
    app.setApplicationName('StructureFinder')
    db_filename = ''
    if len(sys.argv) > 1:
        db_filename = sys.argv[1]
    myapp = StartStructureDB(db_file_name=db_filename)
    myapp.show()
    myapp.raise_()
    myapp.setWindowTitle(f'StructureFinder v{VERSION}')
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    main()
