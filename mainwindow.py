import sys
import threading

from PyQt5.Qt import *
from ui_mainwindow import Ui_MainWindow
from ui_dialog import Ui_Dialog
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