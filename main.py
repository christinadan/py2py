import sys

from PyQt5.Qt import *
from mainwindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    serverport = 12345
    peerid = '127.0.0.1:12345'
    m = MainWindow(firstpeer=peerid, serverport=serverport )
    m.show();
    sys.exit(app.exec_())