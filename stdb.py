from __future__ import print_function

import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTreeWidgetItem

from searcher.cellpicker import get_res_cell, get_cif_cell, get_cif_cell_raw
from searcher.database_handler import StructureTable, DatabaseRequest

uic.compileUiDir('./')
from searcher import filecrawler
from stdb_main import Ui_stdbMainwindow



# TODO:
# - store data from found files in DB
# - more elaborate check if all data is there for the db
# - structure code
# - make file type more flexible. handle .res and .cif equally
# - group structures in measurements
# - list properties of a selected cif file
# - implement relocate cifpath as file open dialog
# - implement progress bar for indexing
# - implement "save on close?" dialog
# - add abort button


class StartStructureDB(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        self.connect_signals_and_slots()
        self.statusBar().showMessage('Ready')
        self.ui.cifList_treeWidget.hide()
        self.ui.properties_treeWidget.hide()
        self.ui.relocate_lineEdit.hide()
        self.dbfilename = 'test.sqlite'
        print(self.dbfilename)
        try:
            os.remove(self.dbfilename)
        except:
            pass
        self.structures = StructureTable(self.dbfilename)
        self.db = DatabaseRequest(self.dbfilename)
        self.db.initialize_db()
        self.show()

    def connect_signals_and_slots(self):
        self.ui.importDatabaseButton.clicked.connect(self.import_database)
        self.ui.importDirButton.clicked.connect(self.import_cif_dirs)
        #self.ui.actionExit.triggered.connect(QtGui.QGuiApplication.quit)
        self.ui.cifList_treeWidget.clicked.connect(self.show_properties)
        # for later use to implement relocation of whole database:
        # self.ui.cifList_treeWidget.doubleClicked.connect(self.relocate)

    def show_properties(self, str):
        """
        This slot show the properties of a cif file in the properties widget
        """
        self.ui.properties_treeWidget.show()
        print(str)

    def relocate(self):
        self.ui.relocate_lineEdit.show()

    def import_database(self):
        print('foo')
        fname = QFileDialog.getOpenFileName(self, 'Open File', '')
        print(fname)
        self.dbfilename = fname[0]
        self.structures = StructureTable(self.dbfilename)
        self.ui.cifList_treeWidget.show()
        for i in self.structures:
            strTree = QTreeWidgetItem(self.ui.cifList_treeWidget)
            strTree.setText(0, i[1])
            self.ui.cifList_treeWidget.resizeColumnToContents(0)
            self.ui.cifList_treeWidget.resizeColumnToContents(1)
            print(i)

    def import_cif_dirs(self):
        #fname = QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        # fname = "D:/GitHub/StructureDB/test-data"
        fname = os.path.abspath("/Users/daniel/Downloads")
        #fname = os.path.abspath("test-data")
        files = filecrawler.create_file_list(str(fname), endings='cif')
        self.ui.cifList_treeWidget.show()
        # TODO: implement multiple cells in one cif file:
        n = 1
        for dirn in files:
            dirn = dirn[0]
            print(dirn, '#')
            filename = os.path.split(dirn)[-1]
            path = os.path.dirname(dirn)
            structure_id = n
            with open(dirn, mode='r') as f:
                cell = get_cif_cell_raw(filename=f)[1:]
            if cell and filename and path:
                print(cell, '##') #print(path, filename, structure_id)
                measurement_id = self.structures.fill_measuremnts_table(filename, structure_id)
                self.structures.fill_structures_table(path, filename, structure_id, measurement_id)
                self.structures.fill_cell_table(structure_id, cell)
                strTree = QTreeWidgetItem(self.ui.cifList_treeWidget)
                strTree.setText(0, filename)
                strTree.setText(1, dirn)
                n += 1
                self.ui.cifList_treeWidget.resizeColumnToContents(0)
                self.ui.cifList_treeWidget.resizeColumnToContents(1)
        self.ui.relocate_lineEdit.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = StartStructureDB()
    myapp.show()
    myapp.raise_()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit()
