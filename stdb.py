from __future__ import print_function

import os
import sys
import time

from PyQt5 import uic, Qt3DExtras
from PyQt5.QtCore import pyqtSlot, QSize
from PyQt5.QtGui import QColor, QVector3D, QSurface
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTreeWidgetItem

from lattice import lattice
from opengl.moleculegl import MyScene
from searcher import filecrawler
from searcher.database_handler import StructureTable, DatabaseRequest
from searcher.filecrawler import fill_db_tables
from searcher.fileparser import Cif
from stdb_main import Ui_stdbMainwindow

uic.compileUiDir('./')


"""
TODO:
- make progress bar for indexer and file opener
- structure code
- make 3D model from atoms
- make file type more flexible. handle .res and .cif equally
- group structures in measurements
- list properties of a selected cif file
- implement progress bar for indexing
- implement "save on close?" dialog
- add abort button for indexer
- recognize already indexed files
- search for strings to get a result for a persons name, add person to db
------------
- Cif() should always return the complete dictionary
- the alternate cif keywords should contain the same as the new ones
- Cif() is given to the database handler and the handler goes through all the items and
  does SQL = '''insert into residuals (?)
                values (cifkeys)
                '''.format('?, '*len(keys())
"""


class StartStructureDB(QMainWindow):
    #changedValue = pyqtSignal('QString')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        self.connect_signals_and_slots()
        self.statusBar().showMessage('Ready')
        self.ui.cifList_treeWidget.show()
        self.ui.cifList_treeWidget.hideColumn(2)
        # self.ui.cellSearchEdit.hide()
        self.dbfilename = 'test.sqlite'
        self.ui.centralwidget.setMinimumSize(1200, 500)
        self.showMaximized()
        try:
            # TODO: don't do in future:
            os.remove(self.dbfilename)
        except:
            pass
        self.structures = StructureTable(self.dbfilename)
        self.db = DatabaseRequest(self.dbfilename)
        self.db.initialize_db()
        # The treewidget with the cif list:
        self.str_tree = QTreeWidgetItem(self.ui.cifList_treeWidget)
        self.show()
        #self.display_molecule()
        self.full_list = True  # indicator if the full structures list is shown


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
        #camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        camera.lens().setOrthographicProjection(-16.0, 16.0, -9.0, 9.0, -1.0, 600.0)
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


    def connect_signals_and_slots(self):
        self.ui.importDatabaseButton.clicked.connect(self.import_database)
        self.ui.importDirButton.clicked.connect(self.import_cif_dirs)
        self.ui.searchLineEDit.textChanged.connect(self.search_cell)
        # self.ui.actionExit.triggered.connect(QtGui.QGuiApplication.quit)
        self.ui.cifList_treeWidget.clicked.connect(self.show_properties)
        self.ui.cifList_treeWidget.selectionModel().currentChanged.connect(self.show_properties)
        #self.ui.cifList_treeWidget.doubleClicked.connect(self.show_properties)


    @pyqtSlot('QModelIndex')
    def show_properties(self, item):
        """
        This slot shows the properties of a cif file in the properties widget

        _space_group_symop_operation_xyz oder _symmetry_equiv_pos_as_xyz
        """
        # self.ui.properties_treeWidget.show()
        structure_id = item.sibling(item.row(), 2).data()
        self.show_props(structure_id)

    def show_props(self, structure_id):
        cell = self.structures.get_cell_by_id(structure_id)
        a, b, c, alpha, beta, gamma = 0, 0, 0, 0, 0, 0
        if cell:
            a, b, c, alpha, beta, gamma = cell[0], cell[1], cell[2], cell[3], cell[4], cell[5]
        if a:
            self.ui.aLineEdit.setText("{:>5.4f}".format(a))
        if b:
            self.ui.bLineEdit.setText("{:>5.4f}".format(b))
        if c:
            self.ui.cLineEdit.setText("{:>5.4f}".format(c))
        if alpha:
            self.ui.alphaLineEdit.setText("{:>5.4f}".format(alpha))
        if beta:
            self.ui.betaLineEdit.setText("{:>5.4f}".format(beta))
        if gamma:
            self.ui.gammaLineEdit.setText("{:>5.4f}".format(gamma))
        try:
            self.ui.wR2LineEdit.setText("{:>5.4f}".format(
                self.structures.get_residuals(structure_id, '_refine_ls_wR_factor_ref')))
        except ValueError:
            pass
        try:
            self.ui.r1LineEdit.setText("{:>5.4f}".format(
                self.structures.get_residuals(structure_id, '_refine_ls_R_factor_gt')))
        except ValueError:
            pass
        self.ui.zLineEdit.setText("{}".format(
            self.structures.get_residuals(structure_id, '_cell_formula_units_Z')))
        self.ui.sumFormulaLineEdit.setText("{}".format(
            self.structures.get_residuals(structure_id, '_chemical_formula_sum')))
        self.ui.reflTotalLineEdit.setText("{}".format(
            self.structures.get_residuals(structure_id, '_diffrn_reflns_number')))
        self.ui.goofLineEdit.setText("{}".format(
            self.structures.get_residuals(structure_id, '_refine_ls_goodness_of_fit_ref')))
        self.ui.SpaceGroupLineEdit.setText("{}".format(
            self.structures.get_residuals(structure_id, '_space_group_name_H_M_alt')))

    @pyqtSlot('QString')
    def search_cell(self, search_string):
        """
        searches db for given cell via the cell volume
        
        8.4009  10.4848  11.8979  94.7910 103.0250 108.5480
        
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
            idlist = self.structures.find_by_volume(volume)
            # print(idlist)
            searchresult = self.structures.get_all_structure_names(idlist)
        except ValueError:
            if not self.full_list:
                self.show_full_list()
            return False
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
        fname = QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        #fname = "/Users/daniel/Documents/Strukturen/Miriam/IKms_cf_08_Ni(mes)(cod)PF/FINAL/"
        # fname = "D:/GitHub/StructureDB/test-data"
        # fname = os.path.abspath("/Users/daniel/Downloads")
        # fname = os.path.abspath("../")
        if not fname:
            return False
        self.ui.cifList_treeWidget.show()
        # TODO: implement multiple cells in one cif file:
        n = 1
        times = []
        for filepth in filecrawler.create_file_list(str(fname), endings='cif'):
            if not filepth.is_file():
                continue
            filename = filepth.name
            path = str(filepth.parents[0])
            structure_id = n
            time2 = time.clock()
            cif = Cif(filepth)
            time3 = time.clock()
            diff2 = time3 - time2
            times.append(diff2)
            if not cif.ok:
                continue
            if cif and filename and path:
                fill_db_tables(cif, filename, path, structure_id, self.structures)
                self.add_table_row(filename, path, str(n))
                n += 1
                if n % 200 == 0:
                    self.structures.database.commit_db(".")
        print('Parsed {} cif files in {} s'.format(n, round(sum(times), 2)))
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        #self.ui.cifList_treeWidget.resizeColumnToContents(1)
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
