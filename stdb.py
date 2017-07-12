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

import os
import sys
import tempfile
import time
import re
import pprint
from pathlib import Path
from string import Template

import shutil

import PyQt5
from PyQt5 import uic, QtWidgets
from PyQt5.QtWebEngine import QtWebEngine
from PyQt5.QtCore import pyqtSlot, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTreeWidgetItem
from math import radians, sin

import mol_file_writer
import searcher
from apex import apeximporter
from constants import celltxt
from lattice import lattice
from pymatgen.core.mat_lattice import Lattice
from searcher import filecrawler, misc
from searcher.database_handler import StructureTable
from searcher.fileparser import Cif
uic.compileUiDir('./')
from stdb_main import Ui_stdbMainwindow


"""
TODO:
- Import APEX2/3 database
Als user bruker: psql -U bruker -f /Users/Shared/dkdumpall.sql BAXSdb
Eventuell geht das auch als user daniel, aber mit -U bruker 
- add rightclick: copy unit cell on unit cell field
- get sum formula from atom type and occupancy  _atom_site_occupancy, _atom_site_type_symbol
- try to find a .p4p file to decide if it is a twin, also try to find a TWIN instruction in the cif file
- allow to scan more than one directory. Just add to previous data. Especially for cmd version.
- Make a web interface with python template to view everything also on a web site.
- structure python code
- grow structure. parse symm cards
- make file type more flexible. handle .res and .cif equally
- recognize already indexed files. Add a hash for each file. Make a database search with executemany()
  to get a list of files where hashes exist. Remove results from file crawler. May I need a hash run over 
  all files before the cif parsing run? Or just calc hash, search in db and then decide to parse cif or not? 
- add an advanced search tab where you can search for sum formula, twinning, only elements, names, users, ... 
- add a tab where you can match path name parts to usernames
- the filecrawler should collect the bruker base file name, also for Rigaku? And STOE?
- add measurement specific data to the db, e.g. machine from frame, temp from frame, 
- pressing search in advanced tab will return to base tab with results
- for commandline: crawl to tempfile and write to destfile with unique id
- add a button: open in ...

Advanced tab:
- Exclude checkbox for each entry?
Search for:
- maschine
- Formula
- Atom type
- measurement temp
- r-value region
- disordered? checkbox
- draw structure (with JSME? Acros? Kekule?, https://github.com/ggasoftware/ketcher)
- compare  molecules https://groups.google.com/forum/#!msg/networkx-discuss/gC_-Wc0bRWw/ISRZYFsPCQAJ
  - search algorithms
  http://chemmine.ucr.edu/help/#similarity, https://en.wikipedia.org/wiki/Jaccard_index
"""



class StartStructureDB(QMainWindow):

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
        self.abort_import_button = QtWidgets.QPushButton("Abort (takes a while)")
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setFormat('')
        self.ui.statusbar.addWidget(self.progress)
        self.ui.statusbar.addWidget(self.abort_import_button)
        self.structures = None
        self.show()
        self.full_list = True  # indicator if the full structures list is shown
        self.decide_import = True
        self.connect_signals_and_slots()
        self.view = QWebEngineView()
        QtWebEngine.initialize()
        self.view.load(QUrl.fromLocalFile(os.path.abspath("./displaymol/jsmol.htm")))
        self.view.setMaximumWidth(250)
        self.view.setMaximumHeight(290)
        self.ui.ogllayout.addWidget(self.view)
        self.view.show()
        self.ui.tabWidget.removeTab(1)
        self.ui.tabWidget.removeTab(1)
        self.setWindowIcon(QIcon('./images/monoklin.png'))
        #self.APEX = False

    def connect_signals_and_slots(self):
        """
        Connects the signals and slot.
        The actionExit signal is connected in the ui file.
        """
        # Buttons:
        self.ui.importDatabaseButton.clicked.connect(self.import_cif_database)
        self.ui.saveDatabaseButton.clicked.connect(self.save_database)
        self.ui.importDirButton.clicked.connect(self.import_cif_dirs)
        # Actions:
        self.ui.actionClose_Database.triggered.connect(self.close_db)
        self.ui.actionImport_directory.triggered.connect(self.import_cif_dirs)
        self.ui.actionImport_file.triggered.connect(self.import_cif_database)
        self.ui.actionSave_Database.triggered.connect(self.save_database)
        # self.ui.actionExit.triggered.connect(QtGui.QGuiApplication.quit)
        # Other fields:
        self.ui.txtSearchEdit.textChanged.connect(self.search_text)
        self.ui.searchLineEDit.textChanged.connect(self.search_cell)
        self.ui.cifList_treeWidget.selectionModel().currentChanged.connect(self.get_properties)
        self.abort_import_button.clicked.connect(self.abort_import)
        self.ui.openApexDBButton.clicked.connect(self.import_apex_db)
        # self.ui.cifList_treeWidget.clicked.connect(self.get_properties) # already with selection model():
        # self.ui.cifList_treeWidget.doubleClicked.connect(self.get_properties)

    def progressbar(self, curr: float, min: float, max: float) -> bool:
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
    def close_db(self, copy_on_close=None):
        """
        Closed the current database and erases the list.
        :param copy_on_close: Path to where the file should be copied after close()
        """
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
        self.structures = StructureTable(self.dbfilename)
        self.structures.database.initialize_db()

    @pyqtSlot('QModelIndex', name="get_properties")
    def get_properties(self, item):
        """
        This slot shows the properties of a cif file in the properties widget
        """
        # TODO: _space_group_symop_operation_xyz oder _symmetry_equiv_pos_as_xyz
        if not self.structures.database.cur:
            return False
        structure_id = item.sibling(item.row(), 3).data()
        request = """select * from residuals where StructureId = {}""".format(structure_id)
        dic = self.structures.get_row_as_dict(request)
        self.display_properties(structure_id, dic)
        return True

    def save_database(self) -> bool:
        """
        Saves the database to a certain file. Therefore I have to close the database.
        """
        status = False
        save_name, tst = QFileDialog.getSaveFileName(self, caption='Save File', directory='./', filter="*.sqlite")
        if save_name:
            if shutil._samefile(self.dbfilename, save_name):
                self.statusBar().showMessage("You can not save to the currently opened file!", msecs=5000)
                return False
        if save_name:
            status = self.close_db(save_name)
        if status:
            self.statusBar().showMessage("Database saved.", msecs=5000)

    def display_properties(self, structure_id: str, cif_dic: dict) -> bool:
        """
        Displays the residuals from the cif file
        """
        mol = ' '
        self.clear_fields()
        self.ui.allCifTreeWidget.clear()
        cell = self.structures.get_cell_by_id(structure_id)
        if not cell:
            self.statusBar().showMessage('Not a valid unit cell!', msecs=3000)
            return False
        p = Path("./displaymol/jsmol-template.htm")
        templ = p.read_text(encoding='utf-8', errors='ignore')
        s = Template(templ)
        try:
            tst = mol_file_writer.MolFile(structure_id, self.structures, cell[:6])
            mol = tst.make_mol()
        except (TypeError, KeyError):
            print("Error in structure", structure_id, "while writing mol file.")
            s = Template(' ')
            pass
        content = s.safe_substitute(MyMol=mol)
        p2 = Path("./displaymol/jsmol.htm")
        p2.write_text(data=content, encoding="utf-8", errors='ignore')
        self.view.reload()
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
        self.ui.cellField.setText(celltxt.format(a, alpha, b, beta, c, gamma, volume, ''))
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
            sumdict = searcher.misc.format_sum_formula(cif_dic['_chemical_formula_sum'])
        except KeyError:
            sumdict = {}
        l = ['<html><body>']
        for num, i in enumerate(sumdict):
            if num >1 and num % 8 == 0:
                l.append("<br>")
            l.append("{}<sub>{}</sub>".format(i, sumdict[i]))
        l.append('</body></html>')
        self.ui.formLabel.setText("{}".format("".join(l)))
        self.ui.reflTotalLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_number']))
        self.ui.goofLineEdit.setText("{}".format(cif_dic['_refine_ls_goodness_of_fit_ref']))
        self.ui.SpaceGroupLineEdit.setText("{}".format(cif_dic['_space_group_name_H_M_alt']))
        self.ui.temperatureLineEdit.setText("{}".format(cif_dic['_diffrn_ambient_temperature']))
        self.ui.maxShiftLineEdit.setText("{}".format(cif_dic['_refine_ls_shift_su_max']))
        self.ui.peakLineEdit.setText("{} / {}".format(cif_dic['_refine_diff_density_max'], cif_dic['_refine_diff_density_min']))
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
            d = wavelen/(2*sin(radians(thetamax)))
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
        for key, value in cif_dic.items():
            cif_tree_item = QTreeWidgetItem()
            self.ui.allCifTreeWidget.addTopLevelItem(cif_tree_item)
            cif_tree_item.setText(0, str(key).strip("\n\r "))
            cif_tree_item.setText(1, str(value).strip("\n\r "))
        self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.ui.allCifTreeWidget.resizeColumnToContents(0)
        self.ui.allCifTreeWidget.resizeColumnToContents(1)
        return True

    @pyqtSlot('QString')
    def search_text(self, search_string):
        """
        searches db for given text

        :param search_string:
        :type search_string: str
        :rtype: bool
        """
        idlist = []
        if len(search_string) == 0:
            self.show_full_list()
            return False
        if len(search_string) > 2:
            if not "*" in search_string:
                search_string = '*'+search_string+'*'
        try:
            idlist = self.structures.find_by_strings(search_string)
        except AttributeError as e:
            print(e)
        try:
            self.ui.cifList_treeWidget.clear()
            self.statusBar().showMessage("Found {} entries.".format(len(idlist)), msecs=0)
            for i in idlist:
                # name = i[1]  # .decode("utf-8", "surrogateescape")
                # data = i[2]
                # path = i[3]  # .decode("utf-8", "surrogateescape")
                # id = i[0]
                #self.add_table_row(i[1], i[3], i[2], i[0])
                self.add_table_row(name=i[1], path=i[3], id=i[0], data=i[2])
            self.ui.cifList_treeWidget.sortByColumn(0, 0)
            self.ui.cifList_treeWidget.resizeColumnToContents(0)
        except:
            self.statusBar().showMessage("Nothing found.", msecs=0)

    @pyqtSlot('QString')
    def search_cell(self, search_string):
        """
        searches db for given cell via the cell volume
        
        :param search_string: 
        :return: 
        """
        # TODO: If len(cell) = 1: search for filename and or data_
        try:
            cell = [float(x) for x in search_string.split()]
        except (TypeError, ValueError):
            return False
        if len(cell) != 6:
            self.statusBar().showMessage('Not a valid unit cell!', msecs=2000)
            self.show_full_list()
            return True
        try:
            volume = lattice.vol_unitcell(*cell)
            # First a list of structures where the volume is similar:
            idlist = self.structures.find_by_volume(volume, threshold=0.02)
        except (ValueError, AttributeError):
            if not self.full_list:
                self.show_full_list()
                self.statusBar().showMessage('Found 0 cells.', msecs=3000)
            return False
        # Get a smaller list where only cells are included that have a proper mapping to the input cell:
        idlist2 = []
        if idlist:
            lattice1 = Lattice.from_parameters(*cell)
            self.statusBar().clearMessage()
            for num, i in enumerate(idlist):
                self.progressbar(num, 0, len(idlist)-1)
                request = """select * from cell where StructureId = {}""".format(i)
                dic = self.structures.get_row_as_dict(request)
                try:
                    lattice2 = Lattice.from_parameters(
                        float(dic['a']),
                        float(dic['b']),
                        float(dic['c']),
                        float(dic['alpha']),
                        float(dic['beta']),
                        float(dic['gamma']) )
                except ValueError:
                    continue
                map = lattice1.find_mapping(lattice2, ltol=0.001, atol=0.5, skip_rotation_matrix=True)
                if map:
                    idlist2.append(i)
        searchresult = self.structures.get_all_structure_names(idlist2)
        self.statusBar().showMessage('Found {} cells.'.format(len(idlist2)), msecs=3000)
        self.ui.cifList_treeWidget.clear()
        self.full_list = False
        for i in searchresult:
            self.add_table_row(name=i[3], path=i[2], id=i[0], data=i[4])
            #self.add_table_row(name, path, id)
        self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.ui.cifList_treeWidget.resizeColumnToContents(0)

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
        tree_item = QTreeWidgetItem()
        tree_item.setText(0, name)  # name
        tree_item.setText(1, data)  # data
        tree_item.setText(2, path)  # path
        tree_item.setData(3, 0, id)  # id
        self.ui.cifList_treeWidget.addTopLevelItem(tree_item)

    def import_cif_database(self):
        """
        Import a new database.
        :rtype: bool
        """
        self.tmpfile = False
        self.close_db()
        fname = QFileDialog.getOpenFileName(self, caption='Open File', directory='./', filter="*.sqlite")
        if not fname[0]:
            return False
        print("Opened {}.". format(fname[0]))
        self.dbfilename = fname[0]
        self.structures = StructureTable(self.dbfilename)
        self.show_full_list()
        if not self.structures:
            return False
        return True

    def open_apex_db(self):
        """
        Opens the APEX db to be displayed in the treeview.
        """
        self.APEX = True
        self.apx = apeximporter.ApexDB()
        conn = self.apx.initialize_db()
        return conn

    def import_apex_db(self):
        """
        Imports data from apex into own db
        :return: None
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
        conn = self.open_apex_db()
        cif = Cif()
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
                tst = filecrawler.fill_db_tables(cif=cif, filename=i[8], path=i[11],
                                                 structure_id=n, structures=self.structures)
                if not tst:
                    continue
                self.add_table_row(name=i[8], path=i[11], data=cif.cif_data['data'], id=str(n))
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
        self.ui.statusbar.showMessage('Added {} cif files to database in: {:>2} h, {:>2} m, {:>3.2f} s'.format(n, h, m, s), msecs=0)
        self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        #self.ui.cifList_treeWidget.resizeColumnToContents(1)
        self.structures.populate_fulltext_search_table()
        self.structures.database.commit_db("Committed")
        self.abort_import_button.hide()


    def show_full_list(self):
        """
        Displays the complete list of structures
        [id, meas, path, filename, data]
        :return: 
        """
        self.ui.cifList_treeWidget.clear()
        id = 0
        for i in self.structures.get_all_structure_names():
            id = i[0]
            self.add_table_row(name=i[3], path=i[2], id=i[0], data=i[4])
        mess = "Loaded {} entries.".format(id)
        self.statusBar().showMessage(mess, msecs=5000)
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        self.ui.cifList_treeWidget.sortByColumn(0, 0)
        #self.ui.cifList_treeWidget.resizeColumnToContents(1)
        self.full_list = True

    def import_cif_dirs(self):
        """
        Imports cif files from a certain directory
        :return: None
        """
        self.APEX = False
        self.tmpfile = True
        self.statusBar().showMessage('')
        self.close_db()
        self.start_db()
        fname = QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        if not fname:
            return False
        self.ui.cifList_treeWidget.show()
        self.abort_import_button.show()
        # TODO: implement multiple cells in one cif file:
        n = 1
        min = 0
        num = 0
        time1 = time.clock()
        cif = Cif()
        for filepth in filecrawler.create_file_list(str(fname), ending='cif'):
            if num == 20:
                num = 0
            self.progressbar(num, min, 20)
            if not filepth.is_file():
                continue
            path = str(filepth.parents[0])
            match = False
            if filepth.name == 'xd_geo.cif':  # Exclude xdgeom cif files
                continue
            for ex in filecrawler.excluded_names:
                if re.search(ex, path, re.I):
                    match = True
            if match:
                continue
            try:
                cifok = cif.parsefile(filepth)
            except IndexError:
                continue
            if not cifok:
                continue
            if cif:
                # is the StructureId
                tst = filecrawler.fill_db_tables(cif, filepth.name, path, n, self.structures)
                if not tst:
                    continue
                self.add_table_row(filepth.name, path, cif.cif_data['data'], str(n))
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
        self.ui.statusbar.showMessage('Added {} cif files to database in: {:>2} h, {:>2} m, {:>3.2f} s'.format(n, h, m, s), msecs=0)
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        #self.ui.cifList_treeWidget.resizeColumnToContents(1)
        self.ui.cifList_treeWidget.sortByColumn(0, 0)
        self.structures.populate_fulltext_search_table()
        self.structures.database.commit_db("Committed")
        self.abort_import_button.hide()

    def clear_fields(self):
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

class QmlAusgabe(object):
    def __init__(self, pathToQmlFile="beispiel.qml"):
        #QML-Engine
        self.__appEngine = QQmlApplicationEngine()
        self.__appEngine.load(pathToQmlFile)
        self.__appWindow = self.__appEngine.rootObjects()[0]

    def show(self):
        self.__appWindow.show()


if __name__ == "__main__":
    # later http://www.pyinstaller.org/
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./images/monoklin.png'))
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
