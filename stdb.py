import sys

from PyQt4 import QtCore, QtGui, uic

uic.compileUiDir('./')

from stdb_main import Ui_stdbMainwindow

class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_stdbMainwindow()
        self.ui.setupUi(self)
        
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    myapp.raise_()
    sys.exit(app.exec_())