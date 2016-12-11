from __future__ import print_function

import os
import sys
from os.path import pathsep

from PyQt4 import QtCore, QtGui, uic

from searcher.cellpicker import get_res_cell, get_cif_cell

uic.compileUiDir('./')
from searcher import filecrawler
from stdb_main import Ui_stdbMainwindow

#TODO:
# - store data from found files in DB
# - list properties of a selected cif file
# - implement relocate as file open dialog

class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        self.ui.importFileButton.clicked.connect(self.import_cif)
        self.ui.importDirButton.clicked.connect(self.import_cif_dirs)
        self.statusBar().showMessage('Ready')
        self.ui.actionExit.triggered.connect(QtGui.qApp.quit)
        self.ui.cifList_treeWidget.hide()
        self.ui.properties_treeWidget.hide()
        self.ui.relocate_lineEdit.hide()
        self.ui.cifList_treeWidget.clicked.connect(self.show_properties)
        # for later use to implement relocation of whole database:
        #self.ui.cifList_treeWidget.doubleClicked.connect(self.relocate)

    def show_properties(self, str):
        """
        This slot show the properties of a cif file in the properties widget
        """
        self.ui.properties_treeWidget.show()

    def relocate(self):
        self.ui.relocate_lineEdit.show()

    def import_cif(self):
        print('foo')
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '')
        print(fname)

    def import_cif_dirs(self):
        #fname = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        #fname = "D:/GitHub/StructureDB/test-data"
        fname = "/Users/daniel/GitHub/StructureDB/test-data"
        files = filecrawler.create_file_list(str(fname), endings='cif')
        self.ui.cifList_treeWidget.show()
        # TODO: implement multiple cells in one cif file:
        for dir, file in files:
            a = QtGui.QTreeWidgetItem(self.ui.cifList_treeWidget)
            a.setText(2, dir)
            #print(get_cif_cell(dir+os.path.sep+file))
            #a.setText(1, ' '.join(map(str, get_res_cell(dir+os.path.sep+file))))
            a.setText(1, ' '.join(map(str, get_cif_cell(dir+os.path.sep+file)[0][1:])))
            a.setText(0, file)
        for i, _ in enumerate(files):
            self.ui.cifList_treeWidget.resizeColumnToContents(i)
        self.ui.relocate_lineEdit.hide()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    myapp.raise_()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit()
