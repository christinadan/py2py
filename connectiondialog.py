import sys

from PyQt5.Qt import *
from Generated.ui_dialog import Ui_Dialog

class ConnectionDialog(QDialog):
    
    def __init__(self):
        super(ConnectionDialog, self).__init__()
        global settings 
        settings = QSettings()
		#Use previously used values or uses default values
    	self.localPort = settings.value("localPort", 5678)
    	self.peerHost = settings.value("peerHost", "10.0.0.9")
    	self.peerPort = settings.value("peerPort", 12345)
        
        # Set up the user interface from Creator
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.localPortLineEdit.setText(str(self.localPort))
        
        if self.peerHost == "":
        	self.ui.peerLineEdit.setText("")
        else:
        	self.ui.peerLineEdit.setText(self.peerHost + ":" + str(self.peerPort))

        if settings.value('checked', "false") == "true":
        	self.ui.rememberSettings.setCheckState(Qt.Checked)
        else:
        	self.ui.rememberSettings.setCheckState(Qt.Unchecked)
        self.ui.cancelButton.clicked.connect(self.close) 
        self.ui.connectButton.clicked.connect(self.setHostInfo)

    def setHostInfo(self):
	#Sets new values if user changes it
    	self.localPort = self.ui.localPortLineEdit.text()
    	peerText = self.ui.peerLineEdit.text()

    	if peerText != "" and ":" in peerText:
    			self.peerHost, self.peerPort = self.ui.peerLineEdit.text().split(':')
    	else:
			self.peerHost = "10.0.0.9"
			self.peerPort = 12345


    	if self.ui.rememberSettings.isChecked():
    		settings.setValue('localPort', self.localPort)
    		settings.setValue('peerHost', self.peerHost)
    		settings.setValue('peerPort', self.peerPort)
    		settings.setValue('checked', "true")
    	else:
    		settings.remove('localPort')
    		settings.remove('peerHost')
    		settings.remove('peerPort')
    		settings.remove('checked')

    	self.close()
