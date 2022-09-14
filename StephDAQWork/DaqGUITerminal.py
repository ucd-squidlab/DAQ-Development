# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 11:32:00 2022

@author: Steph
"""

from DaqGUI import Ui_MainWindow

from PyQt5 import QtWidgets

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
