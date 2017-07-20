# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './strf_dbpasswd.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_strfPassword(object):
    def setupUi(self, strfPasswordWindow):
        strfPasswordWindow.setObjectName("strfPasswordWindow")
        strfPasswordWindow.setGeometry(QtCore.QRect(0, 0, 393, 211))
        self.centralwidget = QtWidgets.QWidget(strfPasswordWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.WarnLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.WarnLabel.setFont(font)
        self.WarnLabel.setObjectName("WarnLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.WarnLabel)
        self.Asklabel = QtWidgets.QLabel(self.centralwidget)
        self.Asklabel.setObjectName("Asklabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.Asklabel)
        self.NameLabel = QtWidgets.QLabel(self.centralwidget)
        self.NameLabel.setObjectName("NameLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.NameLabel)
        self.userNameLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.userNameLineEdit.setObjectName("userNameLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.userNameLineEdit)
        self.PasswordLabel = QtWidgets.QLabel(self.centralwidget)
        self.PasswordLabel.setObjectName("PasswordLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.PasswordLabel)
        self.PasswordLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.PasswordLineEdit.setObjectName("PasswordLineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.PasswordLineEdit)
        self.IPLabel = QtWidgets.QLabel(self.centralwidget)
        self.IPLabel.setObjectName("IPLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.IPLabel)
        self.IPlineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.IPlineEdit.setObjectName("IPlineEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.IPlineEdit)
        self.gridLayout_2.addLayout(self.formLayout, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout_2.addItem(spacerItem, 2, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)
        strfPasswordWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(strfPasswordWindow)
        QtCore.QMetaObject.connectSlotsByName(strfPasswordWindow)

    def retranslateUi(self, strfPasswordWindow):
        _translate = QtCore.QCoreApplication.translate
        strfPasswordWindow.setWindowTitle(_translate("strfPassword", "StructureFinder"))
        self.WarnLabel.setText(_translate("strfPassword", "Unable to connect to the APEX database. "))
        self.Asklabel.setText(_translate("strfPassword", "Please give the correct IP adress, username and password."))
        self.NameLabel.setText(_translate("strfPassword", "Username"))
        self.PasswordLabel.setText(_translate("strfPassword", "Password"))
        self.IPLabel.setText(_translate("strfPassword", "IP Adress"))

