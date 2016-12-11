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
        stdbMainwindow.resize(583, 482)
        self.centralwidget = QtGui.QWidget(stdbMainwindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.importFileButton = QtGui.QPushButton(self.centralwidget)
        self.importFileButton.setObjectName(_fromUtf8("importFileButton"))
        self.verticalLayout.addWidget(self.importFileButton)
        self.importDirButton = QtGui.QPushButton(self.centralwidget)
        self.importDirButton.setObjectName(_fromUtf8("importDirButton"))
        self.verticalLayout.addWidget(self.importDirButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.exportButton = QtGui.QPushButton(self.centralwidget)
        self.exportButton.setObjectName(_fromUtf8("exportButton"))
        self.verticalLayout.addWidget(self.exportButton)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.searchButton = QtGui.QPushButton(self.centralwidget)
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.verticalLayout.addWidget(self.searchButton)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.optionsButton = QtGui.QPushButton(self.centralwidget)
        self.optionsButton.setObjectName(_fromUtf8("optionsButton"))
        self.verticalLayout.addWidget(self.optionsButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        stdbMainwindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(stdbMainwindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 583, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.fileMenu = QtGui.QMenu(self.menubar)
        self.fileMenu.setObjectName(_fromUtf8("fileMenu"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        stdbMainwindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(stdbMainwindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        stdbMainwindow.setStatusBar(self.statusbar)
        self.dataDock = QtGui.QDockWidget(stdbMainwindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataDock.sizePolicy().hasHeightForWidth())
        self.dataDock.setSizePolicy(sizePolicy)
        self.dataDock.setMinimumSize(QtCore.QSize(400, 345))
        self.dataDock.setFloating(False)
        self.dataDock.setObjectName(_fromUtf8("dataDock"))
        self.dockWidgetContents_3 = QtGui.QWidget()
        self.dockWidgetContents_3.setObjectName(_fromUtf8("dockWidgetContents_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.cifs_treeWidget = QtGui.QTreeWidget(self.dockWidgetContents_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cifs_treeWidget.sizePolicy().hasHeightForWidth())
        self.cifs_treeWidget.setSizePolicy(sizePolicy)
        self.cifs_treeWidget.setObjectName(_fromUtf8("cifs_treeWidget"))
        self.verticalLayout_2.addWidget(self.cifs_treeWidget)
        self.dataDock.setWidget(self.dockWidgetContents_3)
        stdbMainwindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dataDock)
        self.actionExit = QtGui.QAction(stdbMainwindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionEdit_dataset = QtGui.QAction(stdbMainwindow)
        self.actionEdit_dataset.setObjectName(_fromUtf8("actionEdit_dataset"))
        self.actionUser_manual = QtGui.QAction(stdbMainwindow)
        self.actionUser_manual.setObjectName(_fromUtf8("actionUser_manual"))
        self.actionImport_file = QtGui.QAction(stdbMainwindow)
        self.actionImport_file.setObjectName(_fromUtf8("actionImport_file"))
        self.actionImport_directory = QtGui.QAction(stdbMainwindow)
        self.actionImport_directory.setObjectName(_fromUtf8("actionImport_directory"))
        self.actionExport_Database_s = QtGui.QAction(stdbMainwindow)
        self.actionExport_Database_s.setObjectName(_fromUtf8("actionExport_Database_s"))
        self.actionOptions = QtGui.QAction(stdbMainwindow)
        self.actionOptions.setObjectName(_fromUtf8("actionOptions"))
        self.fileMenu.addAction(self.actionExit)
        self.fileMenu.addAction(self.actionImport_file)
        self.fileMenu.addAction(self.actionImport_directory)
        self.fileMenu.addAction(self.actionExport_Database_s)
        self.fileMenu.addAction(self.actionOptions)
        self.menuEdit.addAction(self.actionEdit_dataset)
        self.menuHelp.addAction(self.actionUser_manual)
        self.menubar.addAction(self.fileMenu.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(stdbMainwindow)
        QtCore.QMetaObject.connectSlotsByName(stdbMainwindow)

    def retranslateUi(self, stdbMainwindow):
        stdbMainwindow.setWindowTitle(_translate("stdbMainwindow", "MainWindow", None))
        self.importFileButton.setText(_translate("stdbMainwindow", "Import File", None))
        self.importDirButton.setText(_translate("stdbMainwindow", "Import Directory", None))
        self.exportButton.setText(_translate("stdbMainwindow", "Export Database(s)", None))
        self.searchButton.setText(_translate("stdbMainwindow", "Cell Search", None))
        self.optionsButton.setText(_translate("stdbMainwindow", "Options", None))
        self.fileMenu.setTitle(_translate("stdbMainwindow", "File", None))
        self.menuEdit.setTitle(_translate("stdbMainwindow", "edit", None))
        self.menuHelp.setTitle(_translate("stdbMainwindow", "help", None))
        self.cifs_treeWidget.headerItem().setText(0, _translate("stdbMainwindow", "file", None))
        self.cifs_treeWidget.headerItem().setText(1, _translate("stdbMainwindow", "cell", None))
        self.cifs_treeWidget.headerItem().setText(2, _translate("stdbMainwindow", "dir", None))
        self.actionExit.setText(_translate("stdbMainwindow", "Exit", None))
        self.actionExit.setShortcut(_translate("stdbMainwindow", "Ctrl+Q", None))
        self.actionEdit_dataset.setText(_translate("stdbMainwindow", "edit dataset", None))
        self.actionUser_manual.setText(_translate("stdbMainwindow", "user manual", None))
        self.actionImport_file.setText(_translate("stdbMainwindow", "Import file", None))
        self.actionImport_directory.setText(_translate("stdbMainwindow", "Import directory", None))
        self.actionExport_Database_s.setText(_translate("stdbMainwindow", "Export Database(s)", None))
        self.actionOptions.setText(_translate("stdbMainwindow", "Options", None))

