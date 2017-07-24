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

from PyQt5 import QtCore

from searcher.constants import py36

__metaclass__ = type  # use new-style classes

import sys

import time
import math
import os
import shutil
import string
import tempfile

if py36:
    """Only import this if Python 3.6 is used."""
    from PyQt5.QtWebEngine import QtWebEngine
    from PyQt5.QtWebEngineWidgets import QWebEngineView

import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtQml
import PyQt5.QtWidgets
import PyQt5.uic

import pathlib

import apex.apeximporter
from searcher import constants, misc
import displaymol.mol_file_writer
import lattice.lattice
import pymatgen.core.mat_lattice
import searcher.filecrawler
import searcher.fileparser


PyQt5.uic.compileUiDir('./gui')
from gui.strf_main import Ui_stdbMainwindow
from gui.strf_dbpasswd import Ui_PasswdDialog

"""
TODO:
- VCredist 2015 https://www.microsoft.com/de-de/download/details.aspx?id=48145
  and 2010 https://www.microsoft.com/de-de/download/details.aspx?id=5555
- add rightclick: copy unit cell on unit cell field
- get sum formula from atom type and occupancy  _atom_site_occupancy, _atom_site_type_symbol
- allow to scan more than one directory. Just add to previous data. Especially for cmd version.
- Make a web interface with python template to view everything also on a web site.
- add an advanced search tab where you can search for sum formula, twinning, only elements, names, users, ...
- grow structure.
  
Search for:
- draw structure (with JSME? Acros? Kekule?, https://github.com/ggasoftware/ketcher)
- compare  molecules https://groups.google.com/forum/#!msg/networkx-discuss/gC_-Wc0bRWw/ISRZYFsPCQAJ
  - search algorithms
  http://chemmine.ucr.edu/help/#similarity, https://en.wikipedia.org/wiki/Jaccard_index
"""


class StartStructureDB(PyQt5.QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        self.statusBar().showMessage('Ready', msecs=8000)
        self.ui.cifList_treeWidget.show()
        self.ui.cifList_treeWidget.hideColumn(3)
        self.dbfdesc = None
        self.dbfilename = None
        self.tmpfile = False  # indicates wether a tmpfile or any other db file is used
        self.ui.centralwidget.setMinimumSize(1200, 500)
        self.abort_import_button = PyQt5.QtWidgets.QPushButton("Abort (takes a while)")
        self.progress = PyQt5.QtWidgets.QProgressBar(self)
        self.progress.setFormat('')
        self.ui.statusbar.addWidget(self.progress)
        self.ui.statusbar.addWidget(self.abort_import_button)
        self.structures = None
        self.show()
        self.full_list = True  # indicator if the full structures list is shown
        self.decide_import = True
        self.connect_signals_and_slots()
        if py36:
            self.init_webview()
        #self.ui.tabWidget.removeTab(2)
        self.ui.tabWidget.setCurrentIndex(0)
        self.setWindowIcon(PyQt5.QtGui.QIcon('./icons/monoklin.png'))
        self.uipass = Ui_PasswdDialog()
        self.structureId = ''

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
        self.ui.ad_SearchPushButton.clicked.connect(self.advanced_search)
        # Actions:
        self.ui.actionClose_Database.triggered.connect(self.close_db)
        self.ui.actionImport_directory.triggered.connect(self.import_cif_dirs)
        self.ui.actionImport_file.triggered.connect(self.import_cif_database)
        self.ui.actionSave_Database.triggered.connect(self.save_database)
        # self.ui.actionExit.triggered.connect(QtGui.QGuiApplication.quit)
        # Other fields:
        if py36:
            self.ui.txtSearchEdit.textChanged.connect(self.search_text)
        else:
            self.ui.txtSearchEdit.setText("For full test search, use a modern Operating system.")
        self.ui.searchCellLineEDit.textChanged.connect(self.search_cell)
        self.ui.cifList_treeWidget.selectionModel().currentChanged.connect(self.get_properties)

    @PyQt5.QtCore.pyqtSlot(name="advanced_search")
    def advanced_search(self):
        """
        Combines all the search fields

        If cell results:
            all other results are only part of the cell results.
        
        """
        results = []
        cell = self.ui.ad_unitCellLineEdit.text()
        elincl = self.ui.ad_elementsIncLineEdit.text()
        elexcl = self.ui.ad_elementsExLineEdit.text()
        txt = self.ui.ad_textsearch.text()
        if elincl:
            results.extend(self.search_elements(elincl))
            #print(elincl, results)
        if cell and len(cell.split()) == 6:
            results.extend(self.search_cell(cell))
        if txt:
            results.extend(self.structures.find_by_strings(txt))
        if elexcl:
            elexcl = self.search_elements(elexcl)
            #print('ecluded:', elexcl)
        print('results', results)
        print(list(set(elexcl) & set(results)))

    def passwd_handler(self):
        """
        Manages the QDialog buttons on the password dialog.
        """
        d = PyQt5.QtWidgets.QDialog()
        self.passwd = self.uipass.setupUi(d)
        ip_dialog = d.exec()
        if ip_dialog == 1:  # Accepted
            print(self.uipass.userNameLineEdit.text())
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
        QtWebEngine.initialize()
        self.view.load(PyQt5.QtCore.QUrl.fromLocalFile(os.path.abspath("./displaymol/jsmol.htm")))
        self.view.setMaximumWidth(250)
        self.view.setMaximumHeight(290)
        self.ui.ogllayout.addWidget(self.view)
        self.view.show()

    @PyQt5.QtCore.pyqtSlot(name="cell_state_changed")
    def cell_state_changed(self):
        """
        Searches a cell but with diffeent loos or strict option.
        """
        self.search_cell(self.ui.searchCellLineEDit.text())

    def import_cif_dirs(self):
        searcher.filecrawler.put_cifs_in_db(self)

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

    @PyQt5.QtCore.pyqtSlot(name="close_db")
    def close_db(self, copy_on_close: str = None) -> bool:
        """
        Closed the current database and erases the list.
        :param copy_on_close: Path to where the file should be copied after close()
        """
        self.ui.searchCellLineEDit.clear()
        self.ui.txtSearchEdit.clear()
        self.ui.cifList_treeWidget.clear()
        try:
            self.structures.database.cur.close()
        except:
            pass
        try:
            self.structures.database.con.close()
        except:
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

    @PyQt5.QtCore.pyqtSlot(name="abort_import")
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
        self.structures = searcher.database_handler.StructureTable(self.dbfilename)
        self.structures.database.initialize_db()

    @PyQt5.QtCore.pyqtSlot('QModelIndex', name="get_properties")
    def get_properties(self, item):
        """
        This slot shows the properties of a cif file in the properties widget
        """
        if not self.structures.database.cur:
            return False
        structure_id = item.sibling(item.row(), 3).data()
        request = """select * from residuals where StructureId = {}""".format(structure_id)
        dic = self.structures.get_row_as_dict(request)
        self.display_properties(structure_id, dic)
        self.structureId = structure_id
        return True

    def save_database(self) -> bool:
        """
        Saves the database to a certain file. Therefore I have to close the database.
        """
        status = False
        save_name, tst = PyQt5.QtWidgets.QFileDialog.getSaveFileName(self, caption='Save File', directory='./', filter="*.sqlite")
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
        if event.type() == PyQt5.QtCore.QEvent.MouseButtonDblClick:
            if self.structureId:
                cell = ''
                try:
                    cell = "{:>8.6} {:>8.6} {:>8.6} {:>8.6} {:>8.6} {:>8.6}"\
                        .format(*self.structures.get_cell_by_id(self.structureId))
                except:
                    pass
                clipboard = PyQt5.QtWidgets.QApplication.clipboard()
                clipboard.setText(cell)
            return True
        elif event.type() == PyQt5.QtCore.QEvent.MouseButtonPress:
            if event.buttons() == QtCore.Qt.RightButton:
                #print("rightbutton")
            #print("Mouse pressed")
                return True
        return False

    def display_properties(self, structure_id: str, cif_dic: dict) -> bool:
        """
        Displays the residuals from the cif file
        """
        self.clear_fields()
        self.ui.allCifTreeWidget.clear()
        cell = self.structures.get_cell_by_id(structure_id)
        if not cell:
            self.statusBar().showMessage('Not a valid unit cell!', msecs=3000)
            return False
        if py36:
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
        #self.ui.cellField.setMinimumWidth(180)
        self.ui.cellField.setText(constants.celltxt.format(a, alpha, b, beta, c, gamma, volume, ''))
        self.ui.cellField.installEventFilter(self)
        self.ui.cellField.setToolTip("Double click on cell to copy to clipboard.")
        try:
            self.ui.wR2LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_wR_factor_ref']))
        except ValueError:
            pass
        try:  # R1:
            self.ui.r1LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_R_factor_gt']))
        except ValueError:
            pass
        self.ui.zLineEdit.setText("{}".format(cif_dic['_cell_formula_units_Z']))
        try:
            sumform = searcher.misc.format_sum_formula(cif_dic['_chemical_formula_sum'])
        except KeyError:
            sumform = ''
        self.ui.formLabel.setText("{}".format(sumform))
        self.ui.reflTotalLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_number']))
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
            d = wavelen/(2 * math.sin(math.radians(thetamax)))
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
        atoms_item = PyQt5.QtWidgets.QTreeWidgetItem()
        self.ui.allCifTreeWidget.addTopLevelItem(atoms_item)
        atoms_item.setText(0, 'Atoms')
        try:
            for at in self.structures.get_atoms_table(structure_id, cartesian=False):
                data_cif_tree_item = PyQt5.QtWidgets.QTreeWidgetItem(atoms_item)
                self.ui.allCifTreeWidget.addTopLevelItem(atoms_item)
                data_cif_tree_item.setText(1, '{:<8.8s}\t {:<4s}\t {:>8.5f}\t {:>8.5f}\t {:>8.5f}'.format(*at))
        except TypeError:
            pass
        for key, value in cif_dic.items():
            if key == "_shelx_res_file":
                continue
            cif_tree_item = PyQt5.QtWidgets.QTreeWidgetItem()
            self.ui.allCifTreeWidget.addTopLevelItem(cif_tree_item)
            cif_tree_item.setText(0, str(key))
            cif_tree_item.setText(1, str(value))
        shelx_tree_item = PyQt5.QtWidgets.QTreeWidgetItem()
        shelx_data_item = PyQt5.QtWidgets.QTreeWidgetItem(shelx_tree_item)
        self.ui.allCifTreeWidget.addTopLevelItem(shelx_tree_item)
        shelx_tree_item.setText(0, '_shelx_res_file')
        shelx_data_item.setText(1, cif_dic['_shelx_res_file'])
        #self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.ui.allCifTreeWidget.resizeColumnToContents(0)
        self.ui.allCifTreeWidget.resizeColumnToContents(1)
        return True

    def display_molecule(self, cell: list, structure_id: str) -> None:
        """
        """
        mol = ' '
        p = pathlib.Path("./displaymol/jsmol-template.htm")
        templ = p.read_text(encoding='utf-8', errors='ignore')
        s = string.Template(templ)
        try:
            tst = displaymol.mol_file_writer.MolFile(structure_id, self.structures, cell[:6])
            mol = tst.make_mol()
        except (TypeError, KeyError):
            #print("Error in structure", structure_id, "while writing mol file.")
            s = string.Template(' ')
            pass
        content = s.safe_substitute(MyMol=mol)
        p2 = pathlib.Path("./displaymol/jsmol.htm")
        p2.write_text(data=content, encoding="utf-8", errors='ignore')
        self.view.reload()

    @PyQt5.QtCore.pyqtSlot('QString')
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
            return False      # No database cursor
        idlist = []
        if len(search_string) == 0:
            self.show_full_list()
            return False
        if len(search_string) >= 2:
            if not "*" in search_string:
                search_string = '*'+search_string+'*'
        try:
            idlist = self.structures.find_by_strings(search_string)
        except AttributeError as e:
            print(e)
        try:
            #self.ui.cifList_treeWidget.clear()
            self.statusBar().showMessage("Found {} entries.".format(len(idlist)))
            for i in idlist:
                # name = i[1]  # .decode("utf-8", "surrogateescape")
                # data = i[2]
                # path = i[3]  # .decode("utf-8", "surrogateescape")
                # id = i[0]
                #self.add_table_row(i[1], i[3], i[2], i[0])
                self.add_table_row(name=i[1], path=i[3], id=i[0], data=i[2])
            #self.ui.cifList_treeWidget.sortByColumn(0, 0)
            self.ui.cifList_treeWidget.resizeColumnToContents(0)
        except:
            self.statusBar().showMessage("Nothing found.")

    @PyQt5.QtCore.pyqtSlot('QString')
    def search_cell(self, search_string: str) -> bool:
        """
        searches db for given cell via the cell volume
        """
        if self.ui.moreResultsCheckBox.isChecked():
            threshold = 0.06
            ltol = 0.08
            atol = 1.5
        else:
            threshold = 0.03
            ltol = 0.001
            atol = 1
        self.ui.txtSearchEdit.clear()
        try:
            if not self.structures:
                return False  # Empty database
        except:
            return False      # No database cursor
        if not search_string:
            self.full_list = True
            self.show_full_list()
        try:
            cell = [float(x) for x in search_string.split()]
        except (TypeError, ValueError):
            return False
        if len(cell) != 6:
            self.statusBar().showMessage('Not a valid unit cell!', msecs=3000)
            #self.show_full_list()
            return True
        try:
            volume = lattice.lattice.vol_unitcell(*cell)
            # First a list of structures where the volume is similar:
            idlist = self.structures.find_by_volume(volume, threshold)
        except (ValueError, AttributeError):
            if not self.full_list:
                self.ui.cifList_treeWidget.clear()
                self.statusBar().showMessage('Found 0 cells.')
            return False
        # Get a smaller list where only cells are included that have a proper mapping to the input cell:
        idlist2 = []
        if idlist:
            lattice1 = pymatgen.core.mat_lattice.Lattice.from_parameters(*cell)
            self.statusBar().clearMessage()
            for num, i in enumerate(idlist):
                self.progressbar(num, 0, len(idlist)-1)
                request = """select * from cell where StructureId = {}""".format(i)
                dic = self.structures.get_row_as_dict(request)
                try:
                    lattice2 = pymatgen.core.mat_lattice.Lattice.from_parameters(
                        float(dic['a']),
                        float(dic['b']),
                        float(dic['c']),
                        float(dic['alpha']),
                        float(dic['beta']),
                        float(dic['gamma']) )
                except ValueError:
                    continue
                map = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
                if map:
                    idlist2.append(i)
        if not idlist2:
            self.ui.cifList_treeWidget.clear()
            self.statusBar().showMessage('Found 0 cells.', msecs=0)
            return False
        searchresult = self.structures.get_all_structure_names(idlist2)
        self.statusBar().showMessage('Found {} cells.'.format(len(idlist2)))
        self.ui.cifList_treeWidget.clear()
        self.full_list = False
        for i in searchresult:
            self.add_table_row(name=i[3], path=i[2], id=i[0], data=i[4])
            #self.add_table_row(name, path, id)
        #self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.ui.cifList_treeWidget.resizeColumnToContents(0)

    def search_elements(self, elements) -> list:
        """
        list(set(l).intersection(l2))
        """
        self.statusBar().showMessage('')
        formula = []
        res = []
        try:
            formula = misc.get_list_of_elements(elements)
        except KeyError:
            self.statusBar().showMessage('Error: Wrong list of Elements!', msecs=5000)
        try:
            res = self.structures.find_by_elements(formula)
        except AttributeError:
            pass
        return list(res)

    def add_table_row(self, name: str, path: str, data: bytes, id: str) -> None:
        """
        Adds a line to the search results table
        :type name: str, bytes
        :type path: str, bytes
        :type id: str
        :return: None
        """
        if isinstance(name, bytes):
            name = name.decode("utf-8", "surrogateescape")
        if isinstance(path, bytes):
            path = path.decode("utf-8", "surrogateescape")
        if isinstance(data, bytes):
            data = data.decode("utf-8", "surrogateescape")
        tree_item = PyQt5.QtWidgets.QTreeWidgetItem()
        tree_item.setText(0, name)  # name
        tree_item.setText(1, data)  # data
        tree_item.setText(2, path)  # path
        tree_item.setData(3, 0, id)  # id
        self.ui.cifList_treeWidget.addTopLevelItem(tree_item)

    def import_cif_database(self) -> bool:
        """
        Import a new database.
        """
        self.tmpfile = False
        self.close_db()
        fname = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self, caption='Open File', directory='./', filter="*.sqlite")
        if not fname[0]:
            return False
        print("Opened {}.". format(fname[0]))
        self.dbfilename = fname[0]
        self.structures = searcher.database_handler.StructureTable(self.dbfilename)
        self.show_full_list()
        if not self.structures:
            return False
        return True

    def open_apex_db(self, user: str, password: str, host: str) -> bool:
        """
        Opens the APEX db to be displayed in the treeview.
        """
        self.apx = apex.apeximporter.ApexDB()
        connok = False
        try:
            connok = self.apx.initialize_db(user, password, host)
        except:
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
        min = 0
        num = 0
        time1 = time.clock()
        conn = self.open_apex_db(user, password, host)
        if not conn:
            self.abort_import_button.hide()
            return False
        cif = searcher.fileparser.Cif()
        if conn:
            for i in self.apx.get_all_data():
                if num == 20:
                    num = 0
                self.progressbar(num, min, 20)
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
                cif.cif_data['_diffrn_reflns_av_R_equivalents'] = i[21] #rint
                cif.cif_data['_diffrn_reflns_av_unetI/netI'] = i[22] #rsig
                cif.cif_data['_diffrn_reflns_number'] = i[23]
                comp = i[26]
                if comp:
                    cif.cif_data['_diffrn_measured_fraction_theta_max'] = comp/100
                tst = searcher.filecrawler.fill_db_tables(cif=cif, filename=i[8], path=i[12],
                                                          structure_id=n, structures=self.structures)
                if not tst:
                    continue
                self.add_table_row(name=i[8], data=i[8], path=i[12], id=str(n))
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
        #self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        #self.ui.cifList_treeWidget.resizeColumnToContents(1)
        if py36:
            self.structures.populate_fulltext_search_table()
        self.structures.database.commit_db("Committed")
        self.abort_import_button.hide()


    def show_full_list(self) -> None:
        """
        Displays the complete list of structures
        [id, meas, path, filename, data]
        """
        self.ui.cifList_treeWidget.clear()
        id = 0
        if not self.structures:
            return
        for i in self.structures.get_all_structure_names():
            id = i[0]
            self.add_table_row(name=i[3], path=i[2], id=i[0], data=i[4])
        mess = "Loaded {} entries.".format(id)
        self.statusBar().showMessage(mess, msecs=5000)
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        #self.ui.cifList_treeWidget.sortByColumn(0, 0)
        #self.ui.cifList_treeWidget.resizeColumnToContents(1)
        self.full_list = True

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


if __name__ == "__main__":
    # later http://www.pyinstaller.org/
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(PyQt5.QtGui.QIcon('./icons/monoklin.png'))
    app.setApplicationName("StructureFinder")
    app.setApplicationDisplayName("StructureFinder")
    myapp = StartStructureDB()
    myapp.show()
    myapp.raise_()
    myapp.setWindowTitle("StructureFinder")
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit()
