# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './stdb_main.ui'
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

class Ui_stdbMainwindow(object):
    def setupUi(self, stdbMainwindow):
        stdbMainwindow.setObjectName(_fromUtf8("stdbMainwindow"))
        stdbMainwindow.resize(471, 474)
        self.centralwidget = QtGui.QWidget(stdbMainwindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.verticalLayout.addWidget(self.pushButton_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pushButton_3 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.verticalLayout.addWidget(self.pushButton_3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.pushButton_4 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.verticalLayout.addWidget(self.pushButton_4)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.mdiArea = QtGui.QMdiArea(self.centralwidget)
        self.mdiArea.setObjectName(_fromUtf8("mdiArea"))
        self.horizontalLayout.addWidget(self.mdiArea)
        stdbMainwindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(stdbMainwindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 471, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        stdbMainwindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(stdbMainwindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        stdbMainwindow.setStatusBar(self.statusbar)

        self.retranslateUi(stdbMainwindow)
        QtCore.QMetaObject.connectSlotsByName(stdbMainwindow)

    def retranslateUi(self, stdbMainwindow):
        stdbMainwindow.setWindowTitle(_translate("stdbMainwindow", "MainWindow", None))
        self.pushButton_2.setText(_translate("stdbMainwindow", "import", None))
        self.pushButton_3.setText(_translate("stdbMainwindow", "export", None))
        self.pushButton.setText(_translate("stdbMainwindow", "add new", None))
        self.pushButton_4.setText(_translate("stdbMainwindow", "search", None))

