# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SerialConnect.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ser_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 390)
        self.close = QtWidgets.QDialogButtonBox(Dialog)
        self.close.setGeometry(QtCore.QRect(50, 350, 341, 32))
        self.close.setOrientation(QtCore.Qt.Horizontal)
        self.close.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.close.setObjectName("close")
        self.GPIB = QtWidgets.QFrame(Dialog)
        self.GPIB.setEnabled(False)
        self.GPIB.setGeometry(QtCore.QRect(0, 40, 191, 211))
        self.GPIB.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.GPIB.setFrameShadow(QtWidgets.QFrame.Raised)
        self.GPIB.setObjectName("GPIB")
        self.label_2 = QtWidgets.QLabel(self.GPIB)
        self.label_2.setGeometry(QtCore.QRect(80, 0, 66, 19))
        self.label_2.setObjectName("label_2")
        self.Serial = QtWidgets.QFrame(Dialog)
        self.Serial.setGeometry(QtCore.QRect(200, 40, 191, 211))
        self.Serial.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Serial.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Serial.setObjectName("Serial")
        self.label_3 = QtWidgets.QLabel(self.Serial)
        self.label_3.setGeometry(QtCore.QRect(80, 0, 66, 19))
        self.label_3.setObjectName("label_3")
        self.lineEdit = QtWidgets.QLineEdit(self.Serial)
        self.lineEdit.setGeometry(QtCore.QRect(10, 40, 171, 27))
        self.lineEdit.setObjectName("lineEdit")
        self.DevPath = QtWidgets.QLabel(self.Serial)
        self.DevPath.setGeometry(QtCore.QRect(10, 20, 81, 19))
        self.DevPath.setObjectName("DevPath")
        self.BaudRate = QtWidgets.QLabel(self.Serial)
        self.BaudRate.setGeometry(QtCore.QRect(10, 70, 71, 19))
        self.BaudRate.setObjectName("BaudRate")
        self.label_6 = QtWidgets.QLabel(self.Serial)
        self.label_6.setGeometry(QtCore.QRect(10, 120, 151, 19))
        self.label_6.setObjectName("label_6")
        self.BaudRte = QtWidgets.QLineEdit(self.Serial)
        self.BaudRte.setGeometry(QtCore.QRect(10, 90, 113, 27))
        self.BaudRte.setObjectName("BaudRte")
        self.CommandTest = QtWidgets.QLineEdit(self.Serial)
        self.CommandTest.setGeometry(QtCore.QRect(10, 140, 171, 27))
        self.CommandTest.setObjectName("CommandTest")
        self.connectSerial = QtWidgets.QPushButton(self.Serial)
        self.connectSerial.setGeometry(QtCore.QRect(30, 170, 121, 27))
        self.connectSerial.setCheckable(False)
        self.connectSerial.setChecked(False)
        self.connectSerial.setObjectName("connectSerial")
        self.InstrumentOutput = QtWidgets.QTextBrowser(Dialog)
        self.InstrumentOutput.setGeometry(QtCore.QRect(10, 280, 381, 61))
        self.InstrumentOutput.setObjectName("InstrumentOutput")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 260, 151, 20))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        self.close.accepted.connect(Dialog.accept) # type: ignore
        self.close.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Instrument Connection"))
        self.label_2.setText(_translate("Dialog", "GPIB"))
        self.label_3.setText(_translate("Dialog", "Serial"))
        self.DevPath.setText(_translate("Dialog", "Device Path"))
        self.BaudRate.setText(_translate("Dialog", "Baud Rate"))
        self.label_6.setText(_translate("Dialog", "Test Command"))
        self.BaudRte.setText(_translate("Dialog", "9600"))
        self.CommandTest.setText(_translate("Dialog", "*IDN?"))
        self.connectSerial.setText(_translate("Dialog", "Connect and Test"))
        self.label.setText(_translate("Dialog", "Instrument Output:"))
