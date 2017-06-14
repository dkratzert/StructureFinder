from __future__ import print_function

import os
import sys
import time

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTreeWidgetItem
from math import radians, sin

from lattice import lattice
from pymatgen.core.mat_lattice import Lattice
from searcher import filecrawler
from searcher.database_handler import StructureTable, DatabaseRequest
from searcher.filecrawler import fill_db_tables
from searcher.fileparser import Cif
uic.compileUiDir('./')
from stdb_main import Ui_stdbMainwindow


"""
TODO:
- make cell field looking like cell in APEX3
- allow to scan more than one directory. Just add to previous data
- Add save button.
- structure code
- make 3D model from atoms
- make file type more flexible. handle .res and .cif equally
- group structures in measurements
- add abort button for indexer
- recognize already indexed files. Add a hash for each file. Make a database search with executemany()
  to get a list of files where hashes exist. Remove results from file crawler. May I need a hash run over 
  all files before the cif parsing run? Or just calc hash, search in db and then decide to parse cif or not? 
- search for strings to get a result for a persons name, add person to db
- add an advanced search tab where you can search for sum formula, only elements, names, users, ... 
- add a file browser where you can match the local path 
- add progress bar for cell search
- add a tab where you can match path name parts to usernames
- the filecrawler should collect the bruker base file name, also for Rigaku? And STOE?
- add measurement specific data to the db, e.g. machine from frame, temp from frame, 
- pressing search in advanced tab will return to base tab with results

- Fix the 3D crap:
    def display_molecule(self):
        # TODO: Make this work.
        view = Qt3DExtras.Qt3DWindow()
        view.defaultFrameGraph().setClearColor(QColor('lightgray'))
        q3dWidget = QWidget.createWindowContainer(view)
        screenSize = view.screen().size()
        q3dWidget.setMinimumSize(QSize(100, 100))
        q3dWidget.setMaximumSize(screenSize)
        self.ui.openglVlayout.addWidget(q3dWidget)
        s = MyScene()
        scene = s.createScene()
        print('#scene')
        # // Camera
        camera = view.camera()
        # lens = Qt3DRender.QCameraLens()
        camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        #camera.lens().setOrthographicProjection(-16.0, 16.0, -9.0, 9.0, -1.0, 600.0)
        # camera.setUpVector(QVector3D(0, 1.0, 0))
        camera.setPosition(QVector3D(0, 0, 140.0))  # Entfernung
        camera.setViewCenter(QVector3D(0, 0, 0))
        print('#camera')
        # // For camera controls
        camController = Qt3DExtras.QOrbitCameraController(scene)
        camController.setLinearSpeed(-30.0)
        camController.setLookSpeed(-480.0)
        camController.setCamera(camera)
        view.setRootEntity(scene)
        print('view#')
        view.show()
"""


class StartStructureDB(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        self.connect_signals_and_slots()
        self.statusBar().showMessage('Ready')
        self.ui.cifList_treeWidget.show()
        self.ui.cifList_treeWidget.hideColumn(2)
        self.dbfilename = 'test.sqlite'
        self.ui.centralwidget.setMinimumSize(1200, 500)
        #self.showMaximized()
        try:
            # TODO: don't do in future:
            os.remove(self.dbfilename)
        except:
            pass
        self.progress = QtWidgets.QProgressBar(self)
        self.ui.statusbar.addWidget(self.progress)
        self.structures = StructureTable(self.dbfilename)
        self.structures.database.initialize_db()
        # The treewidget with the cif list:
        self.str_tree = QTreeWidgetItem(self.ui.cifList_treeWidget)
        self.show()
        #self.display_molecule()
        self.full_list = True  # indicator if the full structures list is shown

    def connect_signals_and_slots(self):
        """
        Connects the signals and slot.
        The actionExit signal is connected in the ui file.
        """
        self.ui.importDatabaseButton.clicked.connect(self.import_database)
        self.ui.importDirButton.clicked.connect(self.import_cif_dirs)
        self.ui.searchLineEDit.textChanged.connect(self.search_cell)
        # self.ui.actionExit.triggered.connect(QtGui.QGuiApplication.quit)
        self.ui.cifList_treeWidget.clicked.connect(self.get_properties)
        self.ui.cifList_treeWidget.selectionModel().currentChanged.connect(self.get_properties)
        #self.ui.cifList_treeWidget.doubleClicked.connect(self.get_properties)
        self.ui.actionClose_Database.triggered.connect(self.close_db)
        self.ui.actionImport_directory.triggered.connect(self.import_cif_dirs)
        self.ui.actionImport_file.triggered.connect(self.import_database)

    def progressbar(self, curr, min, max):
        """
        """
        self.progress.setValue(curr)
        self.progress.setMaximum(max)
        self.progress.setMinimum(min)
        self.progress.show()
        if curr == max:
            self.progress.hide()

    @pyqtSlot(name="close_db")
    def close_db(self):
        """
        Closed the current database and erases the list.
        """
        self.structures.database.cur.close()
        self.structures.database.con.close()
        #self.structures = StructureTable(self.dbfilename)
        #self.structures.database.initialize_db()
        self.ui.cifList_treeWidget.clear()

    @pyqtSlot('QModelIndex', name="get_properties")
    def get_properties(self, item):
        """
        This slot shows the properties of a cif file in the properties widget

        _space_group_symop_operation_xyz oder _symmetry_equiv_pos_as_xyz
        """
        # self.ui.properties_treeWidget.show()
        structure_id = item.sibling(item.row(), 2).data()
        request = """select * from residuals where StructureId = {}""".format(structure_id)
        dic = self.structures.get_row_as_dict(request)
        self.display_properties(structure_id, dic)

    def display_properties(self, structure_id, cif_dic):
        """
        Displays the residuals from the cif file
        """
        cell = self.structures.get_cell_by_id(structure_id)
        if not cif_dic:
            return False
        a, b, c, alpha, beta, gamma, volume = 0, 0, 0, 0, 0, 0, 0
        if cell:
            a, b, c, alpha, beta, gamma, volume = cell[0], cell[1], cell[2], cell[3], cell[4], cell[5], cell[6]
        self.ui.cellField.setText(
            r"""
            <html><head/><body>
            <table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" 
                   cellspacing="2" cellpadding="2">
                <tr>
                    <td><p align="left" ><span style=" font-style:italic;">a</span> = </p></td>
                    <td><p align="right">{:>8.3f} Å, </p></td>
                    <td><p align="left"><span style="font-style:italic;">&alpha;</span> = </p></td> 
                    <td><p align="right">{:<8.3f}° </p></td>
                </tr>
                <tr>
                    <td><p align="left"><span style=" font-style:italic;">b</span> = </p></td>
                    <td><p align="right">{:>8.3f} Å, </p></td>
                    <td><p align="left"><span style=" font-style:italic;">&beta;</span> = </p></td> 
                    <td><p align="right">{:<8.3f}° </p></td>
                </tr>
                <tr>
                    <td><p align="left"><span style=" font-style:italic;">c</span> = </p></td>
                    <td><p align="right">{:>8.3f} Å, </p></td>
                    <td><p align="left"><span style=" font-style:italic;">&gamma;</span> = </p></td> 
                    <td><p align="right">{:<8.3f}° </p></td>
                </tr>
            </table>
            Volume = {:8.3f} Å
            </body></html>
            """.format(a, alpha, b, beta, c, gamma, volume, '')
        )
        try:
            self.ui.wR2LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_wR_factor_ref']))
        except ValueError:
            pass
        try:  # R1:
            self.ui.r1LineEdit.setText("{:>5.4f}".format(cif_dic['_refine_ls_R_factor_gt']))
        except ValueError:
            pass
        self.ui.zLineEdit.setText("{}".format(cif_dic['_cell_formula_units_Z']))
        self.ui.sumFormulaLineEdit.setText("{}".format(cif_dic['_chemical_formula_sum']))
        self.ui.reflTotalLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_number']))
        self.ui.goofLineEdit.setText("{}".format(cif_dic['_refine_ls_goodness_of_fit_ref']))
        self.ui.SpaceGroupLineEdit.setText("{}".format(cif_dic['_space_group_name_H_M_alt']))
        self.ui.temperatureLineEdit.setText("{}".format(cif_dic['_diffrn_ambient_temperature']))
        self.ui.maxShiftLineEdit.setText("{}".format(cif_dic['_refine_ls_shift_su_max']))
        self.ui.peakLineEdit.setText("{} / {}".format(cif_dic['_refine_diff_density_max'], cif_dic['_refine_diff_density_min']))
        self.ui.rintLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_av_R_equivalents']))
        self.ui.rsigmaLineEdit.setText("{}".format(cif_dic['_diffrn_reflns_av_unetI_netI']))
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
        return True

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
            if not self.full_list:
                self.show_full_list()
            return True
        try:
            volume = lattice.vol_unitcell(*cell)
            # First a list of structures where the volume is similar:
            idlist = self.structures.find_by_volume(volume, threshold=0.03)
        except ValueError:
            if not self.full_list:
                self.show_full_list()
            return False
        # Get a smaller list where only cells are included that have a proper mapping to the input cell:
        idlist2 = []
        if idlist:
            lattice1 = Lattice.from_parameters(*cell)
            for num, i in enumerate(idlist):
                self.progressbar(num, 0, len(idlist)-1)
                request = """select * from cell where StructureId = {}""".format(i)
                dic = self.structures.get_row_as_dict(request)
                cell2 = [dic['a'], dic['b'], dic['c'], dic['alpha'], dic['beta'], dic['gamma']]
                cell2 = [float(x) for x in cell2]
                lattice2 = Lattice.from_parameters(*cell2)
                map = lattice1.find_mapping(lattice2, ltol=0.2, atol=1, skip_rotation_matrix=True)
                if map:
                    idlist2.append(i)
        searchresult = self.structures.get_all_structure_names(idlist2)
        self.ui.cifList_treeWidget.clear()
        self.full_list = False
        for i in searchresult:
            name = i[3]  # .decode("utf-8", "surrogateescape")
            path = i[2]  # .decode("utf-8", "surrogateescape")
            id = i[0]
            self.add_table_row(name, path, id)
        self.ui.cifList_treeWidget.resizeColumnToContents(0)

    def add_table_row(self, name, path, id):
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
        self.str_tree = QTreeWidgetItem(self.ui.cifList_treeWidget)
        self.str_tree.setText(0, name)  # name
        self.str_tree.setText(1, path)  # path
        self.str_tree.setData(2, 0, id)  # id

    def import_database(self):
        """
        Import a new database.
        :return: 
        """
        fname = QFileDialog.getOpenFileName(self, caption='Open File', directory='./')
        if not fname[0]:
            return False
        print("Opened {}.". format(fname[0]))
        self.dbfilename = fname[0]
        self.structures = StructureTable(self.dbfilename)
        #self.ui.cifList_treeWidget.show()
        self.show_full_list()
        if not self.structures:
            return False

    def show_full_list(self):
        """
        Displays the complete list of structures
        :return: 
        """
        self.ui.cifList_treeWidget.clear()
        self.str_tree = QTreeWidgetItem(self.ui.cifList_treeWidget)
        id = 0
        for i in self.structures.get_all_structure_names():
            name = i[3]
            path = i[2]#.decode("utf-8", "surrogateescape")
            id = i[0]
            self.add_table_row(name, path, id)
        print("Loaded {} entries.".format(id))
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        self.full_list = True

    def import_cif_dirs(self):
        """
        Imports cif files from a certain directory
        :return: None
        """
        # TODO: support excludes: mit filepath.parent in excludes = ('.olex', 'report', 'Report')
        fname = QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        if not fname:
            return False
        self.ui.cifList_treeWidget.show()
        # TODO: implement multiple cells in one cif file:
        n = 1
        min = 0
        time1 = time.clock()
        for num, filepth in enumerate(filecrawler.create_file_list(str(fname), endings='cif')):
            if num == 20:
                num = 0
            self.progressbar(num, min, 20)
            if not filepth.is_file():
                continue
            filename = filepth.name
            path = str(filepth.parents[0])
            structure_id = n
            cif = Cif(filepth)
            if not cif.ok:
                continue
            if cif and filename and path:
                fill_db_tables(cif, filename, path, structure_id, self.structures)
                self.add_table_row(filename, path, str(n))
                n += 1
                if n % 200 == 0:
                    self.structures.database.commit_db(".")
        time2 = time.clock()
        diff = time2 - time1
        self.progress.hide()
        self.ui.statusbar.showMessage('Parsed {} cif files in {} s'.format(n, round(diff, 2)))
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        self.ui.cifList_treeWidget.resizeColumnToContents(1)
        self.structures.database.commit_db("Committed")


class QmlAusgabe(object):
    def __init__(self, pathToQmlFile="beispiel.qml"):
        #QML-Engine
        self.__appEngine = QQmlApplicationEngine()
        self.__appEngine.load(pathToQmlFile)
        self.__appWindow = self.__appEngine.rootObjects()[0]

    def show(self):
        self.__appWindow.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = StartStructureDB()
    myapp.show()
    myapp.raise_()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit()
