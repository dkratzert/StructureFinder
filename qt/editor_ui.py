# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editor.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_notepad(object):
    def setupUi(self, notepad):
        notepad.setObjectName(_fromUtf8("notepad"))
        notepad.resize(471, 474)
        self.centralwidget = QtGui.QWidget(notepad)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.openButton = QtGui.QPushButton(self.centralwidget)
        self.openButton.setObjectName(_fromUtf8("openButton"))
        self.horizontalLayout.addWidget(self.openButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.button_save = QtGui.QPushButton(self.centralwidget)
        self.button_save.setEnabled(False)
        self.button_save.setObjectName(_fromUtf8("button_save"))
        self.horizontalLayout.addWidget(self.button_save)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.closeButton = QtGui.QPushButton(self.centralwidget)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.editor_window = QtGui.QTextEdit(self.centralwidget)
        self.editor_window.setObjectName(_fromUtf8("editor_window"))
        self.verticalLayout.addWidget(self.editor_window)
        notepad.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(notepad)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 471, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        notepad.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(notepad)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        notepad.setStatusBar(self.statusbar)

        self.retranslateUi(notepad)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), notepad.close)
        QtCore.QMetaObject.connectSlotsByName(notepad)

    def retranslateUi(self, notepad):
        notepad.setWindowTitle(_translate("notepad", "MainWindow", None))
        self.openButton.setText(_translate("notepad", "open file", None))
        self.button_save.setText(_translate("notepad", "save file", None))
        self.closeButton.setText(_translate("notepad", "exit", None))

