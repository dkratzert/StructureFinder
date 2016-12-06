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
        self.ui.editor_window.textChanged.connect(self.enable_save)
        self.filename = None
    
    #def file_dialog(self):
    #    """
    #    The file open dialog
    #    """
    #    fd = QtGui.QFileDialog(self)
    #    from os.path import isfile
    #    self.filename = fd.getOpenFileName()
    #    if isfile(self.filename):
    #        import codecs
    #        txt = codecs.open(self.filename, 'r', 'utf-8').read()
    #        self.ui.editor_window.setPlainText(txt)

    def enable_save(self):
        self.ui.button_save.setEnabled(True)

    def file_save(self):
        """
        """
        from os.path import isfile
        if isfile(self.filename):
            import codecs
            with codecs.open(self.filename, 'w', 'utf-8') as fileopj:
                fileopj.write(unicode(self.ui.editor_window.toPlainText()))
                
    def file_dialog(self):
        response = False
        # buttons texts
        SAVE = 'Save'
        DISCARD = 'Discard'
        CANCEL = 'Cancel'
        # if we have changes then ask about them
        if self.ui.button_save.isEnabled() and self.filename:
            message = QtGui.QMessageBox(self)
            message.setText('What to do about unsaved changes ?')
            message.setWindowTitle('Notepad')
            message.setIcon(QtGui.QMessageBox.Question)
            message.addButton(SAVE, QtGui.QMessageBox.AcceptRole)
            message.addButton(DISCARD, QtGui.QMessageBox.DestructiveRole)
            message.addButton(CANCEL, QtGui.QMessageBox.RejectRole)
            message.setDetailedText('Unsaved changes in file: ' + str(self.filename))
            message.exec_()
            response = message.clickedButton().text()
            # save  file
            if response == SAVE:
                self.file_save()
                self.ui.button_save.setEnabled(False)
            # discard changes
            elif response == DISCARD:
                self.ui.button_save.setEnabled(False)
        # if we didn't cancelled show the file dialogue
        if response != CANCEL:
            fd = QtGui.QFileDialog(self)
            self.filename = fd.getOpenFileName()
            from os.path import isfile
            if isfile(self.filename):
                import codecs
                s = codecs.open(self.filename,'r','utf-8').read()
                self.ui.editor_window.setPlainText(s)
                self.ui.button_save.setEnabled(False)

 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    myapp.activateWindow()
    myapp.raise_()
    sys.exit(app.exec_())
    