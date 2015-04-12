# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 160)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.localPortLineEdit = QtWidgets.QLineEdit(Dialog)
        self.localPortLineEdit.setObjectName("localPortLineEdit")
        self.gridLayout_2.addWidget(self.localPortLineEdit, 0, 1, 1, 1)
        self.localLabel = QtWidgets.QLabel(Dialog)
        self.localLabel.setObjectName("localLabel")
        self.gridLayout_2.addWidget(self.localLabel, 0, 0, 1, 1)
        self.peerLabel = QtWidgets.QLabel(Dialog)
        self.peerLabel.setObjectName("peerLabel")
        self.gridLayout_2.addWidget(self.peerLabel, 1, 0, 1, 1)
        self.peerLineEdit = QtWidgets.QLineEdit(Dialog)
        self.peerLineEdit.setObjectName("peerLineEdit")
        self.gridLayout_2.addWidget(self.peerLineEdit, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.rememberSettings = QtWidgets.QCheckBox(Dialog)
        self.rememberSettings.setObjectName("rememberSettings")
        self.horizontalLayout.addWidget(self.rememberSettings)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_2.addWidget(self.cancelButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.connectButton = QtWidgets.QPushButton(Dialog)
        self.connectButton.setObjectName("connectButton")
        self.horizontalLayout_2.addWidget(self.connectButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Connection Setup"))
        self.localLabel.setText(_translate("Dialog", "Local Port"))
        self.peerLabel.setText(_translate("Dialog", "Peer-IP:Port (Optional)"))
        self.rememberSettings.setText(_translate("Dialog", "Remember these settings"))
        self.cancelButton.setText(_translate("Dialog", "Cancel"))
        self.connectButton.setText(_translate("Dialog", "Connect"))

