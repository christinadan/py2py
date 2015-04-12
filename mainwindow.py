import sys
import threading

from PyQt5.Qt import *
from ui_mainwindow import Ui_MainWindow
from connectiondialog import ConnectionDialog
from random import *
from btfiler import *

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Set up the user interface from Creator
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Make some local modifications to UI
        self.ui.fileTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.fileTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.ui.fileTableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)

        self.connectionPopup()

    def connectionPopup(self):
        self.connectionDialog = ConnectionDialog()
        self.connectionDialog.exec_()
