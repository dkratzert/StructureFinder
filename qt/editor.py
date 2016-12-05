import sys
from PyQt4 import QtCore, QtGui
from editor_ui import Ui_notepad
from fileinput import filename

class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_notepad()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.openButton, QtCore.SIGNAL('clicked()'), self.file_dialog)
        QtCore.QObject.connect(self.ui.button_save,QtCore.SIGNAL("clicked()"), self.file_save)
    
    
    def file_dialog(self):
        """
        The file open dialog
        """
        fd = QtGui.QFileDialog(self)
        from os.path import isfile
        self.filename = fd.getOpenFileName()
        if isfile(self.filename):
            import codecs
            txt = codecs.open(self.filename, 'r', 'utf-8').read()
            self.ui.editor_window.setPlainText(txt)


    def file_save(self):
        """
        """
        from os.path import isfile
        if isfile(self.filename):
            import codecs
            with codecs.open(self.filename, 'w', 'utf-8') as fileopj:
                fileopj.write(unicode(self.ui.editor_window.toPlainText()))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    myapp.activateWindow()
    myapp.raise_()
    sys.exit(app.exec_())
    