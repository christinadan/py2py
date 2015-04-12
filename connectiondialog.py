import sys

from PyQt5.Qt import *
from Generated.ui_dialog import Ui_Dialog

class ConnectionDialog(QDialog):
    
    def __init__(self):
        super(ConnectionDialog, self).__init__()
        global settings 
        settings = QSettings()
    	localPort = settings.value("localPort", 5678)
    	peerHost = settings.value("peerHost", "10.0.0.9")
    	peerPort = settings.value("peerPort", 1234)
        
        # Set up the user interface from Creator
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.localPortLineEdit.setText(str(localPort))
        if peerHost == "":
        	self.ui.peerLineEdit.setText("")
        else:
        	self.ui.peerLineEdit.setText(peerHost + ":" + str(peerPort))

        if settings.value('checked', "false") == "true":
        	self.ui.rememberSettings.setCheckState(Qt.Checked)
        else:
        	self.ui.rememberSettings.setCheckState(Qt.Unchecked)
        self.ui.cancelButton.clicked.connect(self.close) 
        self.ui.connectButton.clicked.connect(self.setHostInfo)

    def setHostInfo(self):
    	localPort = self.ui.localPortLineEdit.text()
    	peerText = self.ui.peerLineEdit.text()
    	if peerText != "" and ":" in peerText:
    			peerHost, peerPort = self.ui.peerLineEdit.text().split(':')
    	else:
			peerHost = "10.0.0.9"
			peerPort = 1234


    	if self.ui.rememberSettings.isChecked():
    		settings.setValue('localPort', localPort)
    		settings.setValue('peerHost', peerHost)
    		settings.setValue('peerPort', peerPort)
    		settings.setValue('checked', "true")
    	else:
    		settings.remove('localPort')
    		settings.remove('peerHost')
    		settings.remove('peerPort')
    		settings.remove('checked')

    	self.close()
