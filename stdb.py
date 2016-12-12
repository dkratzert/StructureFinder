from __future__ import print_function

import os
import sys

from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTreeWidgetItem

from searcher.cellpicker import get_res_cell, get_cif_cell
from searcher.database_handler import StructureTable, DatabaseRequest

uic.compileUiDir('./')
from searcher import filecrawler
from stdb_main import Ui_stdbMainwindow


# TODO:
# - store data from found files in DB
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
        self.structures = StructureTable(self.dbfilename)
        self.db = DatabaseRequest(self.dbfilename)
        self.db.initialize_db()
        self.show()

    def connect_signals_and_slots(self):
        self.ui.importFileButton.clicked.connect(self.import_cif)
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

    def relocate(self):
        self.ui.relocate_lineEdit.show()

    def import_cif(self):
        print('foo')
        fname = QFileDialog.getOpenFileName(self, 'Open File', '')
        print(fname)

    def import_cif_dirs(self):
        fname = QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        # fname = "D:/GitHub/StructureDB/test-data"
        # fname = "/Users/daniel/GitHub/StructureDB/test-data"
        files = filecrawler.create_file_list(str(fname), endings='cif')
        self.ui.cifList_treeWidget.show()
        # TODO: implement multiple cells in one cif file:
        n = 1
        for dir, file in files:
            try:
                cell = get_cif_cell(dir + os.path.sep + file)[0][1:]
            except IndexError:
                continue
            self.structures.fill_structures_table(dir, file)
            a = QTreeWidgetItem(self.ui.cifList_treeWidget)
            a.setText(0, file)
            a.setText(1, dir)
            # print(get_cif_cell(dir+os.path.sep+file))
            # a.setText(1, ' '.join(map(str, get_res_cell(dir+os.path.sep+file))))
            # a.setText(2, ' '.join(map(str, get_cif_cell(dir+os.path.sep+file)[0][1:])))
            # print(n, get_cif_cell(dir+os.path.sep+file)[0][1:])
            self.structures.fill_cell_table(n, get_cif_cell(dir + os.path.sep + file)[0][1:])
            n += 1
        for i, _ in enumerate(files):
            self.ui.cifList_treeWidget.resizeColumnToContents(i)
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
