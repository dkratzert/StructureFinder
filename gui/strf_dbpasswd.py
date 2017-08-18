# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/strf_dbpasswd.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PasswdDialog(object):
    def setupUi(self, PasswdDialog):
        PasswdDialog.setObjectName("PasswdDialog")
        PasswdDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PasswdDialog.resize(400, 213)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PasswdDialog.sizePolicy().hasHeightForWidth())
        PasswdDialog.setSizePolicy(sizePolicy)
        PasswdDialog.setSizeGripEnabled(False)
        PasswdDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(PasswdDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.WarnLabel = QtWidgets.QLabel(PasswdDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.WarnLabel.setFont(font)
        self.WarnLabel.setObjectName("WarnLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.WarnLabel)
        self.Asklabel = QtWidgets.QLabel(PasswdDialog)
        self.Asklabel.setObjectName("Asklabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.Asklabel)
        self.NameLabel = QtWidgets.QLabel(PasswdDialog)
        self.NameLabel.setObjectName("NameLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.NameLabel)
        self.userNameLineEdit = QtWidgets.QLineEdit(PasswdDialog)
        self.userNameLineEdit.setObjectName("userNameLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.userNameLineEdit)
        self.PasswordLabel = QtWidgets.QLabel(PasswdDialog)
        self.PasswordLabel.setObjectName("PasswordLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.PasswordLabel)
        self.PasswordLineEdit = QtWidgets.QLineEdit(PasswdDialog)
        self.PasswordLineEdit.setObjectName("PasswordLineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.PasswordLineEdit)
        self.IPLabel = QtWidgets.QLabel(PasswdDialog)
        self.IPLabel.setObjectName("IPLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.IPLabel)
        self.IPlineEdit = QtWidgets.QLineEdit(PasswdDialog)
        self.IPlineEdit.setObjectName("IPlineEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.IPlineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(PasswdDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(PasswdDialog)
        self.buttonBox.accepted.connect(PasswdDialog.accept)
        self.buttonBox.rejected.connect(PasswdDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PasswdDialog)

    def retranslateUi(self, PasswdDialog):
        _translate = QtCore.QCoreApplication.translate
        PasswdDialog.setWindowTitle(_translate("PasswdDialog", "StructureFinder"))
        self.WarnLabel.setText(_translate("PasswdDialog", "Unable to connect to the APEX database. "))
        self.Asklabel.setText(_translate("PasswdDialog", "Please give the correct IP Adress, Username and Password."))
        self.NameLabel.setText(_translate("PasswdDialog", "Username"))
        self.userNameLineEdit.setText(_translate("PasswdDialog", "BrukerPostgreSQL"))
        self.PasswordLabel.setText(_translate("PasswdDialog", "Password"))
        self.PasswordLineEdit.setText(_translate("PasswdDialog", "Bruker-PostgreSQL"))
        self.IPLabel.setText(_translate("PasswdDialog", "IP Adress"))
        self.IPlineEdit.setText(_translate("PasswdDialog", "localhost"))
