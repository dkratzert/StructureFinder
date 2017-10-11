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
from __future__ import print_function

import math
import os
import pathlib
import shutil
import string
import sys
import tempfile
import time
from datetime import date

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import misc.update_check
from apex import apeximporter
from displaymol import mol_file_writer
from lattice import lattice
from misc import update_check
from misc.version import VERSION
from pymatgen.core import mat_lattice
from searcher import constants, misc, filecrawler, database_handler
from searcher.constants import py36
from searcher.fileparser import Cif
from searcher.misc import is_valid_cell, formula_str_to_dict

if py36:
    """Only import this if Python 3.6 is used."""
    from PyQt5.QtWebEngineWidgets import QWebEngineView

__metaclass__ = type  # use new-style classes

"""
TODO:
- Figure out how guest and other users are handled with "Open APEX Database" button.
- disable molecule on windows7 32 bit? Maybe disabling spin helps?
- Improve text search (in cif file)
- refractor put_cifs_in_db()
- Move indexer to extra thread
- sort results by G6 distance
- get sum formula from atom type and occupancy  _atom_site_occupancy, _atom_site_type_symbol
- grow structure.
  
Search for:
- draw structure (with JSME? Acros? Kekule?, https://github.com/ggasoftware/ketcher)
- compare  molecules https://groups.google.com/forum/#!msg/networkx-discuss/gC_-Wc0bRWw/ISRZYFsPCQAJ
  - search algorithms
  http://chemmine.ucr.edu/help/#similarity, https://en.wikipedia.org/wiki/Jaccard_index
"""


class StartStructureDB(QtWidgets.QMainWindow):
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
        self.ui.centralwidget.setMinimumSize(1200, 500)
        self.abort_import_button = QtWidgets.QPushButton("Abort (takes a while)")
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setFormat('')
        self.ui.statusbar.addWidget(self.progress)
        self.ui.statusbar.addWidget(self.abort_import_button)
        self.structures = None
        self.apx = None
        self.structureId = ''
        self.passwd = ''
        self.show()
        self.full_list = True  # indicator if the full structures list is shown
        self.decide_import = True
        self.connect_signals_and_slots()
        # Set both to today() to distinquish between a modified and unmodified date field.
        self.ui.dateEdit1.setDate(QtCore.QDate(date.today()))
        self.ui.dateEdit2.setDate(QtCore.QDate(date.today()))
        if py36:
            molf = pathlib.Path("./displaymol/jsmol.htm")
            molf.write_text(data=' ', encoding="utf-8", errors='ignore')
            self.init_webview()
        else:
            self.ui.tabWidget.removeTab(2)
            self.ui.txtSearchEdit.hide()
            self.ui.txtSearchLabel.hide()
            self.ui.openglview.hide()
        self.ui.tabWidget.setCurrentIndex(0)
        self.setWindowIcon(QtGui.QIcon('./icons/strf.png'))
        self.uipass = Ui_PasswdDialog()
        # self.ui.cifList_treeWidget.sortByColumn(0, 0)
        # Actions for certain gui elements:
        self.ui.cellField.addAction(self.ui.actionCopy_Unit_Cell)
        self.ui.cifList_treeWidget.addAction(self.ui.actionGo_to_All_CIF_Tab)
        if len(sys.argv) > 1:
            try:
                self.dbfilename = sys.argv[1]
                self.structures = database_handler.StructureTable(self.dbfilename)
                self.show_full_list()
            except IndexError:
                pass
        if update_check.is_update_needed(VERSION=VERSION):
            self.statusBar().showMessage('A new Version of StructureFinder is available at '
                                         'https://www.xs3.uni-freiburg.de/research/structurefinder')

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
        self.ui.ad_ShowAllButton.clicked.connect(self.show_full_list)
        # Actions:
        self.ui.actionClose_Database.triggered.connect(self.close_db)
        self.ui.actionImport_directory.triggered.connect(self.import_cif_dirs)
        self.ui.actionImport_file.triggered.connect(self.import_cif_database)
        self.ui.actionSave_Database.triggered.connect(self.save_database)
        self.ui.actionCopy_Unit_Cell.triggered.connect(self.copyUnitCell)
        self.ui.actionGo_to_All_CIF_Tab.triggered.connect(self.on_click_item)
        # Other fields:
        if py36:
            self.ui.txtSearchEdit.textChanged.connect(self.search_text)
        else:
            self.ui.txtSearchEdit.setText("For full test search, use a modern Operating system.")
        self.ui.searchCellLineEDit.textChanged.connect(self.search_cell)
        self.ui.cifList_treeWidget.selectionModel().currentChanged.connect(self.get_properties)
        self.ui.cifList_treeWidget.itemDoubleClicked.connect(self.on_click_item)
        #self.ui.ad_elementsIncLineEdit.textChanged.connect(self.is_element_doubled_incl)
        #self.ui.ad_elementsExclLineEdit.textChanged.connect(self.is_element_doubled_excl)

    def on_click_item(self, item):
        self.ui.tabWidget.setCurrentIndex(1)

    def copyUnitCell(self):
        if self.structureId:
            try:
                cell = "{:>6.3f} {:>6.3f} {:>6.3f} {:>6.3f} {:>6.3f} {:>6.3f}" \
                    .format(*self.structures.get_cell_by_id(self.structureId))
            except Exception:
                return False
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(cell)
            self.ui.statusbar.showMessage('Copied unit cell {} to clip board.'
                                          .format(cell))
        return True

    @QtCore.pyqtSlot(name="advanced_search")
    def advanced_search(self):
        """
        Combines all the search fields. Collects all includes, all excludes ad calculates
        the difference.
        """
        if not self.structures:
            return
        excl = []
        incl = []
        date_results = []
        cell = is_valid_cell(self.ui.ad_unitCellLineEdit.text())
        date1 = self.ui.dateEdit1.text()
        date2 = self.ui.dateEdit2.text()
        elincl = self.ui.ad_elementsIncLineEdit.text().strip(' ')
        elexcl = self.ui.ad_elementsExclLineEdit.text().strip(' ')
        txt = self.ui.ad_textsearch.text().strip(' ')
        txt_ex = self.ui.ad_textsearch_excl.text().strip(' ')
        if date1 != date2:
            date_results = self.find_dates(date1, date2)
        if cell:
            cellres = self.search_cell_idlist(cell)
            incl.append(cellres)
        if elincl:
            incl.append(self.search_elements(elincl))
        if txt:
            if len(txt) >= 2 and "*" not in txt:
                txt = '*' + txt + '*'
            idlist = self.structures.find_by_strings(txt)
            try:
                incl.append([i[0] for i in idlist])
            except(IndexError, KeyError):
                incl.append([idlist])  # only one result
        if elexcl:
            excl.append(self.search_elements(elexcl, anyresult=True))
        if txt_ex:
            if len(txt_ex) >= 2 and "*" not in txt_ex:
                txt_ex = '*' + txt_ex + '*'
            idlist = self.structures.find_by_strings(txt_ex)
            try:
                excl.append([i[0] for i in idlist])
            except(IndexError, KeyError):
                excl.append([idlist])  # only one result
        if incl and incl[0]:
            results = set(incl[0]).intersection(*incl)
            if date_results:
                results = set(date_results).intersection(results)
        else:
            results = date_results
        if not results:
            self.statusBar().showMessage('Found 0 structures.')
            return
        if excl:
            try:
                self.display_structures_by_idlist(list(results - set(misc.flatten(excl))))
            except TypeError:
                return
        else:
            self.display_structures_by_idlist(list(results))

    def display_structures_by_idlist(self, idlist: list or set) -> None:
        """
        Displays the structures with id in results list
        """
        if not idlist:
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
            self.ui.tabWidget.setCurrentIndex(0)

    def passwd_handler(self):
        """
        Manages the QDialog buttons on the password dialog.
        """
        d = QtWidgets.QDialog()
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
        # QtWebEngine.initialize()
        self.view.load(QtCore.QUrl.fromLocalFile(os.path.abspath("./displaymol/jsmol.htm")))
        self.view.setMaximumWidth(250)
        self.view.setMaximumHeight(290)
        self.ui.ogllayout.addWidget(self.view)
        # self.view.show()

    @QtCore.pyqtSlot(name="cell_state_changed")
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
        fname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        if not fname:
            self.progress.hide()
            self.abort_import_button.hide()
        filecrawler.put_cifs_in_db(self, searchpath=fname)
        self.progress.hide()
        self.structures.database.init_textsearch()
        self.structures.populate_fulltext_search_table()
        self.structures.database.commit_db()
        self.ui.cifList_treeWidget.show()
        self.set_columnsize()
        # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        # self.ui.cifList_treeWidget.resizeColumnToContents(1)
        # self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.abort_import_button.hide()

    def progressbar(self, curr: float, min: float, max: float) -> None:
        """
        Displays a progress bar in the status bar.
        """
        self.progress.setValue(curr)
        self.progress.setMaximum(max)
        self.progress.setMinimum(min)
        self.progress.show()
        if curr == max:
            self.progress.hide()

    @QtCore.pyqtSlot(name="close_db")
    def close_db(self, copy_on_close: str = None) -> bool:
        """
        Closed the current database and erases the list.
        :param copy_on_close: Path to where the file should be copied after close()
        """
        self.ui.searchCellLineEDit.clear()
        self.ui.txtSearchEdit.clear()
        self.ui.cifList_treeWidget.clear()
        if py36:
            molf = pathlib.Path("./displaymol/jsmol.htm")
            molf.write_text(data=' ', encoding="utf-8", errors='ignore')
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
            if shutil._samefile(self.dbfilename, copy_on_close):
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

    @QtCore.pyqtSlot(name="abort_import")
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

    @QtCore.pyqtSlot('QModelIndex', name="get_properties")
    def get_properties(self, item):
        """
        This slot shows the properties of a cif file in the properties widget
        """
        if not self.structures.database.cur:
            return False
        structure_id = item.sibling(item.row(), 3).data()
        dic = self.structures.get_row_as_dict(structure_id)
        self.display_properties(structure_id, dic)
        self.structureId = structure_id
        return True

    def save_database(self) -> bool:
        """
        Saves the database to a certain file. Therefore I have to close the database.
        """
        status = False
        save_name, tst = QtWidgets.QFileDialog.getSaveFileName(self, caption='Save File', directory='./',
                                                               filter="*.sqlite")
        if save_name:
            if shutil._samefile(self.dbfilename, save_name):
                self.statusBar().showMessage("You can not save to the currently opened file!", msecs=5000)
                return False
        if save_name:
            status = self.close_db(save_name)
        if status:
            self.statusBar().showMessage("Database saved.", msecs=5000)

    def eventFilter(self, object, event):
        """Event filter for mouse clicks."""
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            self.copyUnitCell()
        elif event.type() == QtCore.QEvent.MouseButtonPress:
            if event.buttons() == QtCore.Qt.RightButton:
                # print("rightbutton")
                return True
        return False

    def display_properties(self, structure_id: str, cif_dic: dict) -> bool:
        """
        Displays the residuals from the cif file
        Measured Refl.
        Independent Refl.
        Reflections Used

        _refine_ls_number_reflns -> unique reflect. (Independent reflections)
        _reflns_number_gt        -> unique über 2sigma (Independent reflections >2sigma)
        """
        self.clear_fields()
        self.ui.allCifTreeWidget.clear()
        cell = self.structures.get_cell_by_id(structure_id)
        if not cell:
            return False
        self.display_molecule(cell, structure_id)
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
        self.ui.cellField.setText(constants.celltxt.format(a, alpha, b, beta, c, gamma, volume, ''))
        self.ui.cellField.installEventFilter(self)
        self.ui.cellField.setToolTip("Double click on 'Unit Cell' to copy to clipboard.")
        try:
            self.ui.wR2LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_wR_factor_ref']))
        except ValueError:
            pass
        try:  # R1:
            if cif_dic['_refine_ls_R_factor_gt']:
                self.ui.r1LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_R_factor_gt']))
            else:
                self.ui.r1LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_R_factor_all']))
        except ValueError:
            pass
        self.ui.zLineEdit.setText("{}".format(cif_dic['_cell_formula_units_Z']))
        try:
            sumform = misc.format_sum_formula(cif_dic['_chemical_formula_sum'])
        except KeyError:
            sumform = ''
        self.ui.formLabel.setText("{}".format(sumform))
        self.ui.reflTotalLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_number']))
        self.ui.uniqReflLineEdit.setText("{}".format(cif_dic['_refine_ls_number_reflns']))
        self.ui.refl2sigmaLineEdit.setText("{}".format(cif_dic['_reflns_number_gt']))
        self.ui.goofLineEdit.setText("{}".format(cif_dic['_refine_ls_goodness_of_fit_ref']))
        self.ui.SpaceGroupLineEdit.setText("{}".format(cif_dic['_space_group_name_H_M_alt']))
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
        try:
            compl = cif_dic['_diffrn_measured_fraction_theta_max'] * 100
            if not compl:
                compl = 0.0
        except TypeError:
            compl = 0.0
        self.ui.completeLineEdit.setText("{:<5.1f}".format(compl))
        self.ui.wavelengthLineEdit.setText("{}".format(wavelen))
        atoms_item = QtWidgets.QTreeWidgetItem()
        self.ui.allCifTreeWidget.addTopLevelItem(atoms_item)
        atoms_item.setText(0, 'Atoms')
        # self.ui.allCifTreeWidget.installEventFilter(self)
        try:
            for at in self.structures.get_atoms_table(structure_id, cartesian=False):
                data_cif_tree_item = QtWidgets.QTreeWidgetItem(atoms_item)
                self.ui.allCifTreeWidget.addTopLevelItem(atoms_item)
                data_cif_tree_item.setText(1, '{:<8.8s}\t {:<4s}\t {:>8.5f}\t {:>8.5f}\t {:>8.5f}'.format(*at))
        except TypeError:
            pass
        for key, value in cif_dic.items():
            if key == "_shelx_res_file":
                continue
            cif_tree_item = QtWidgets.QTreeWidgetItem()
            self.ui.allCifTreeWidget.addTopLevelItem(cif_tree_item)
            cif_tree_item.setText(0, str(key))
            cif_tree_item.setText(1, str(value))
        shelx_tree_item = QtWidgets.QTreeWidgetItem()
        shelx_data_item = QtWidgets.QTreeWidgetItem(shelx_tree_item)
        self.ui.allCifTreeWidget.addTopLevelItem(shelx_tree_item)
        shelx_tree_item.setText(0, '_shelx_res_file')
        shelx_data_item.setText(1, cif_dic['_shelx_res_file'])
        # self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.ui.allCifTreeWidget.resizeColumnToContents(0)
        self.ui.allCifTreeWidget.resizeColumnToContents(1)
        return True

    def display_molecule(self, cell: list, structure_id: str) -> None:
        """
        Creates a html file from a mol file to display the molecule in jsmol-lite
        """
        mol = ' '
        p = pathlib.Path("./displaymol/jsmol-template.htm")
        templ = p.read_text(encoding='utf-8', errors='ignore')
        s = string.Template(templ)
        try:
            tst = mol_file_writer.MolFile(structure_id, self.structures, cell[:6], grow=False)
            mol = tst.make_mol()
        except (TypeError, KeyError):
            # print("Error in structure", structure_id, "while writing mol file.")
            s = string.Template(' ')
            pass
        content = s.safe_substitute(MyMol=mol)
        p2 = pathlib.Path("./displaymol/jsmol.htm")
        p2.write_text(data=content, encoding="utf-8", errors='ignore')
        self.view.reload()

    @QtCore.pyqtSlot('QString')
    def is_element_doubled_incl(self, foo):
        """
        Determines if elements in the lists of included
        and excludes elements are duplicated.
        """
        try:
            incl = formula_str_to_dict(self.ui.ad_elementsIncLineEdit.text())
            excl = formula_str_to_dict(self.ui.ad_elementsExclLineEdit.text())
        except KeyError:
            incl, excl = ('', '')
        for el in incl:
            if el in excl:
                self.ui.ad_elementsIncLineEdit.setText('')

    @QtCore.pyqtSlot('QString')
    def is_element_doubled_excl(self, foo):
        """
        Determines if elements in the lists of included
        and excludes elements are duplicated.
        """
        try:
            incl = formula_str_to_dict(self.ui.ad_elementsIncLineEdit.text())
            excl = formula_str_to_dict(self.ui.ad_elementsExclLineEdit.text())
        except KeyError:
            incl, excl = ('', '')
        for el in incl:
            if el in excl:
                self.ui.ad_elementsExclLineEdit.setText('')

    @QtCore.pyqtSlot('QString')
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

    @QtCore.pyqtSlot('QString')
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
        if self.ui.moreResultsCheckBox.isChecked() or \
                self.ui.ad_moreResultscheckBox.isChecked():
            threshold = 0.08
            ltol = 0.09
            atol = 1.8
        else:
            threshold = 0.03
            ltol = 0.001
            atol = 1
        idlist = []
        try:
            volume = lattice.vol_unitcell(*cell)
            if self.ui.sublattCheckbox.isChecked() or self.ui.ad_superlatticeCheckBox.isChecked():
                # sub- and superlattices:
                for v in [volume * x for x in (0.25, 0.5, 1, 2, 3, 4)]:
                    # First a list of structures where the volume is similar:
                    idlist.extend(self.structures.find_by_volume(v, threshold))
            else:
                idlist = self.structures.find_by_volume(volume, threshold)
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
            for num, i in enumerate(idlist):
                self.progressbar(num, 0, len(idlist) - 1)
                dic = self.structures.get_cell_as_dict(i)
                try:
                    lattice2 = mat_lattice.Lattice.from_parameters(
                            float(dic['a']),
                            float(dic['b']),
                            float(dic['c']),
                            float(dic['alpha']),
                            float(dic['beta']),
                            float(dic['gamma']))
                except ValueError:
                    continue
                mapping = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
                if mapping:
                    # pprint.pprint(map[3])
                    idlist2.append(i)
        return idlist2

    @QtCore.pyqtSlot('QString')
    def search_cell(self, search_string: str) -> bool:
        """
        searches db for given cell via the cell volume
        """
        cell = is_valid_cell(search_string)
        self.ui.txtSearchEdit.clear()
        if not cell:
            if self.ui.searchCellLineEDit.text():
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

    def search_elements(self, elements: str, anyresult: bool = False) -> list:
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
            res = self.structures.find_by_elements(formula, anyresult=anyresult)
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
        tree_item = QtWidgets.QTreeWidgetItem()
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
        fname = QtWidgets.QFileDialog.getOpenFileName(self, caption='Open File', directory='./',
                                                      filter="*.sqlite")
        if not fname[0]:
            return False
        print("Opened {}.".format(fname[0]))
        self.dbfilename = fname[0]
        self.structures = database_handler.StructureTable(self.dbfilename)
        self.show_full_list()
        if not self.structures:
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
        time1 = time.clock()
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
                cif.cif_data['_exptl_crystal_colour'] = i[14]
                cif.cif_data['_exptl_crystal_size_max'] = i[16]
                cif.cif_data['_exptl_crystal_size_mid'] = i[17]
                cif.cif_data['_exptl_crystal_size_min'] = i[18]
                cif.cif_data["_chemical_formula_sum"] = i[25]
                cif.cif_data['_diffrn_reflns_av_R_equivalents'] = i[21]  # rint
                cif.cif_data['_diffrn_reflns_av_unetI/netI'] = i[22]  # rsig
                cif.cif_data['_diffrn_reflns_number'] = i[23]
                comp = i[26]
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
        time2 = time.clock()
        diff = time2 - time1
        self.progress.hide()
        m, s = divmod(diff, 60)
        h, m = divmod(m, 60)
        self.ui.statusbar.showMessage('Added {} APEX entries in: {:>2d} h, {:>2d} m, {:>3.2f} s'
                                      .format(n, int(h), int(m), s), msecs=0)
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
        if not self.structures:
            return
        for i in self.structures.get_all_structure_names():
            structure_id = i[0]
            self.add_table_row(name=i[3], path=i[2], structure_id=i[0], data=i[4])
        mess = "Loaded {} entries.".format(structure_id)
        self.statusBar().showMessage(mess, msecs=5000)
        self.set_columnsize()
        # self.ui.cifList_treeWidget.resizeColumnToContents(0)
        # self.ui.cifList_treeWidget.resizeColumnToContents(1)
        self.full_list = True
        self.ui.tabWidget.setCurrentIndex(0)

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
        self.ui.formLabel.clear()
        self.ui.temperatureLineEdit.clear()
        self.ui.thetaFullLineEdit.clear()
        self.ui.thetaMaxLineEdit.clear()
        self.ui.wavelengthLineEdit.clear()
        self.ui.wR2LineEdit.clear()
        self.ui.zLineEdit.clear()
        self.ui.cCDCNumberLineEdit.clear()
        self.ui.refl2sigmaLineEdit.clear()
        self.ui.uniqReflLineEdit.clear()


class RunIndexerThread(QtCore.QThread):
    def __init__(self, strf):
        """
        Make a new thread instance
        """
        QtCore.QThread.__init__(self)
        self.strf = strf

    def run(self):
        """
        Runs the indexer thread
        """
        filecrawler.put_cifs_in_db(self.strf)


if __name__ == "__main__":
    uic.compileUiDir('./gui')
    from gui.strf_main import Ui_stdbMainwindow
    from gui.strf_dbpasswd import Ui_PasswdDialog

    # later http://www.pyinstaller.org/
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('./icons/strf.png'))
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
