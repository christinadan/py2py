import sys

from PyQt5.Qt import *
from mainwindow import MainWindow

if __name__ == '__main__':
    app = QApplication( sys.argv )
    m = MainWindow()
    m.show();
    sys.exit( app.exec_() )
	