from __future__ import print_function

import sys
from PyQt4 import QtCore, QtGui, uic

uic.compileUiDir('./')
from searcher import filecrawler
from stdb_main import Ui_stdbMainwindow


class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        self.ui.importFileButton.clicked.connect(self.import_cif)
        self.ui.importDirButton.clicked.connect(self.import_cif_dirs)
        self.statusBar().showMessage('Ready')
        self.ui.actionExit.triggered.connect(QtGui.qApp.quit)
        self.ui.cifs_treeWidget.hide()

    def import_cif(self):
        print('foo')
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '')
        print(fname)

    def import_cif_dirs(self):
        #fname = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', '')
        #fname = "D:/GitHub/StructureDB/test-data"
        fname = "/Users/daniel/GitHub/StructureDB/test-data"
        files = filecrawler.create_file_list(str(fname), endings='cif')
        self.ui.cifs_treeWidget.show()
        for dir, file in files:
            a = QtGui.QTreeWidgetItem(self.ui.cifs_treeWidget)
            a.setText(0, dir)
            a.setText(1, file)
        for i, _ in enumerate(files):
            self.ui.cifs_treeWidget.resizeColumnToContents(i)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    myapp.raise_()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit()
