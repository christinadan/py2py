import sys
import threading

from PyQt5.Qt import *
from ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Make some local modifications to UI
        self.ui.fileTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.fileTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.ui.fileTableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)

def main():
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show();
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
