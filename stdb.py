from __future__ import print_function

import os
import sys

import PyQt5
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
# - more elaborate check if all data is there for the db
# - make progress bar for indexer and file opener
# - make text fields in properties widget. not enerving QTreewidget
# - get atoms from cif
# - store atoms in db
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
        self.ui.cifList_treeWidget.hideColumn(2)
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
        # das brauch ich nicht:
        # self.ui.cifList_treeWidget.doubleClicked.connect(self.relocate)
        #self.ui.cifList_treeWidget.doubleClicked.connect(self.show_properties)

    def show_properties(self, item):
        """
        This slot show the properties of a cif file in the properties widget
        """
        self.ui.properties_treeWidget.show()
        cell = self.structures.get_cell_by_id(item.sibling(item.row(), 2).data())
        print(cell)

    def relocate(self):
        self.ui.relocate_lineEdit.show()

    def import_database(self):
        print('foo')
        fname = QFileDialog.getOpenFileName(self, 'Open File', '')
        print(fname)
        self.dbfilename = fname[0]
        self.structures = StructureTable(self.dbfilename)
        self.ui.cifList_treeWidget.show()
        if not self.structures:
            return False
        for i in self.structures.get_all_structure_names():
            #print(i)
            str_tree = QTreeWidgetItem(self.ui.cifList_treeWidget)
            str_tree.setText(0, i[1])  # name
            str_tree.setText(1, i[2])  # path
            str_tree.setData(2, 0, i[0])  # id
            #if len(i[1]) > 10:
        self.ui.cifList_treeWidget.resizeColumnToContents(0)
        self.ui.cifList_treeWidget.resizeColumnToContents(1)


    def import_cif_dirs(self):
        fname = QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        # fname = "D:/GitHub/StructureDB/test-data"
        #fname = os.path.abspath("/Users/daniel/Downloads")
        #fname = os.path.abspath("test-data")
        if not fname:
            return False
        files = filecrawler.create_file_list(str(fname), endings='cif')
        self.ui.cifList_treeWidget.show()
        # TODO: implement multiple cells in one cif file:
        n = 1
        for dirn in files:
            dirn = dirn[0]
            filename = os.path.split(dirn)[-1]
            path = os.path.dirname(dirn)
            structure_id = n
            with open(dirn, mode='r') as f:
                #print(filename)
                try:
                    cell = get_cif_cell_raw(filename=f)[1:]
                except (TypeError, IndexError):
                    print("No cell found. Trying next file...")
                    continue
            if cell and filename and path:
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
        self.structures.database.commit_db("Committed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = StartStructureDB()
    myapp.show()
    myapp.raise_()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit()
