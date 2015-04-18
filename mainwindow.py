import sys
import threading
import os

from PyQt5.Qt import *
from Generated.ui_mainwindow import Ui_MainWindow
from connectiondialog import ConnectionDialog
from random import *
from peerfilemanager import *

class MainWindow( QMainWindow ):
	def __init__( self, hops=2, master=None ):
		super( MainWindow, self ).__init__()
		
		# Set up the user interface from Creator
		self.ui = Ui_MainWindow()
		self.ui.setupUi( self )

		# Make some local modifications to UI
		self.ui.fileList.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch )
		self.ui.fileList.horizontalHeader().setSectionResizeMode( 0, QHeaderView.Interactive )
		self.connectSignals()

		self.connectionPopup()
		#Add signal to do the rest of this in another function on connection dialog close event
		#Initialize connection settings
		self.peer = PeerFileManager( int(self.connectionDialog.localPort) )

		#check IP; if good IP, connect; else, use a default
		self.peer.buildPeers( self.connectionDialog.peerHost, int(self.connectionDialog.peerPort), hops=hops )
		self.updatePeerList()
		self.ui.portLabel.setText('Server Port: ' + self.connectionDialog.localPort)

		t = threading.Thread( target = self.peer.mainLoop, args = [] )
		t.start()

		self.peer.startStabilizer( self.peer.checkLivePeers, 3 )
		self.onTimer()

	def connectSignals(self):
		self.ui.actionUpload.triggered.connect( self.fileSelect )
		self.ui.actionRefresh.triggered.connect( self.onRefresh )
		self.ui.actionDownload.triggered.connect( self.startDownload )
		self.ui.fetchButton.clicked.connect( self.startDownload )
		self.ui.searchButton.clicked.connect( self.onSearch )
		self.ui.searchLineEdit.returnPressed.connect( self.onSearch )
		self.ui.rebuildButton.clicked.connect( self.onRebuild )
		self.ui.clearAllButton.clicked.connect( self.onClearAll )
		
	def connectionPopup(self):
		self.connectionDialog = ConnectionDialog()
		self.connectionDialog.exec_()

	def fileSelect(self):
		fileDialog = QFileDialog( self )
		fileDialog.setLabelText( QFileDialog.Accept, 'Upload' )
		fileDialog.setWindowTitle( 'Choose a File to Upload' )
		if fileDialog.exec_():
			filename = fileDialog.selectedFiles()[0]
		if os.path.getsize(filename) > 25000000: #25 Megabytes
			 msgBox = QMessageBox(self);
			 msgBox.setWindowTitle("py2py");
			 msgBox.setText("File must be 25 Megabytes or less!");
			 msgBox.exec_();
		elif filename != "" and filename:
			self.peer.addLocalFile( str( filename ) )
		self.updateFileList()

	def onTimer( self ):
		#Refresh every 3 seconds
		try:
			# Do things
			self.onRefresh()
		finally:
			QTimer.singleShot(3000, self.onTimer)
		
	def closeEvent(self, event):
		self.peer.shutdown = True
		event.accept() # let the window close
		
	def updatePeerList( self ):
		#If Peer list display has data, delete it then repopulate from self.peer.getPeerIds()
		if len( self.ui.peerList.selectedItems() ) > 0:
			selectedItem = self.ui.peerList.selectedItems()[0].text()
			print selectedItem
		else:
			selectedItem = ""

		if self.ui.peerList.count() > 0:
			self.ui.peerList.clear()

		for p in self.peer.getPeerIds():
			row = self.ui.peerList.currentRow()+1
			self.ui.peerList.insertItem( row, p )
			if p.lstrip().rstrip() == selectedItem.lstrip().rstrip():
				self.ui.peerList.item( row ).setSelected( True )
			
	def updateFileList( self ):
		#If GUI file display has data, delete it then repopulate from self.peer.files
		if len( self.ui.fileList.selectedItems() ) > 0:
			selectedRow = self.ui.fileList.selectedItems()[0].row()
		else:
			selectedRow = -1

		if self.ui.fileList.rowCount() > 0:
			self.ui.fileList.clearContents()
			self.ui.fileList.setRowCount(0)

			
		row = 0
		for f in self.peer.files:
			print f
			p = self.peer.files[f]
			if not p:
				p = '(local)'

			f.rstrip('\/')
			head, tail = os.path.split( f )
			hostItem = QTableWidgetItem( p )
			fileItem = QTableWidgetItem( tail )
			fileItem.setData( Qt.UserRole, f )

			self.ui.fileList.insertRow( row )
			self.ui.fileList.setItem( row, 0, hostItem )
			self.ui.fileList.setItem( row, 1, fileItem )
			row = row + 1

		if selectedRow > -1:
			self.ui.fileList.selectRow( selectedRow )

	def onClearAll(self):
		#Clears the filelist
		self.ui.fileList.clearContents()
		self.ui.fileList.setRowCount(0)

		files = {}
		for f in self.peer.files:
			p = self.peer.files[f]
			if p == None:
				files[f] = p
		self.peer.files = files

		self.updateFileList()

	def removeFile(self, fileToRemove):
		files = {}
		for f in self.peer.files:
			p = self.peer.files[f]
			if f != fileToRemove:
				files[f] = p
		self.peer.files = files

	def onSearch(self):
		#Gets filename from Search field and queries the network using self.peer.sendToPeer
		self.searchTerm = self.ui.searchLineEdit.text()

		for p in self.peer.getPeerIds():
			self.peer.sendToPeer( p, QUERY, "%s %s 4" % ( self.peer.myid, str( self.searchTerm ) ) )
	
	def onDownload(self):
		#Get currently selected file from GUI and retrieve said file from network
		if len( self.ui.fileList.selectedItems() ) > 0:
			selectedRow = self.ui.fileList.selectedItems()[0].row()
		else:
			selectedRow = -1

		if selectedRow > -1:
			hostItem = self.ui.fileList.item( selectedRow, 0 ).text()
			fileItem = self.ui.fileList.item( selectedRow, 1 ).text()
			fileItemPath = self.ui.fileList.item( selectedRow, 1 ).data( Qt.UserRole )
			if hostItem != '(local)':
				host,port = hostItem.split(':')
				resp = self.peer.connectAndSend( host, int(port), FILEGET, str( fileItemPath ) )
				if len( resp ) and resp[0][0] == REPLY:
					if not os.path.exists('Downloads'):
						os.makedirs('Downloads')
					curDir = os.getcwd()
					os.chdir('Downloads')
					fd = file( fileItem, 'wb')
					fd.write( resp[0][1] )
					fd.close()
					self.removeFile( fileItemPath )
					if os.path.isfile( fileItem ):
						self.peer.addLocalFile( os.path.abspath( fileItem ) )
						self.updateFileList()
					os.chdir( curDir )

	def startDownload(self):
		#Starts download in a separate thread
		t = threading.Thread( target = self.onDownload, args = [] )
		t.start()
	
	def onRefresh(self):
		#Update peer and file list
		self.updatePeerList()
		self.updateFileList()
	
	def onRebuild(self):
		#Get peerid from rebuild field and rebuild peer list using self.peer.buildPeers
		peer = self.ui.rebuildLineEdit.text()
		peer = peer.lstrip().rstrip()

		try:
			if peer != "":
				host,port = peer.split(':')
				self.peer.buildPeers( host, int(port), hops=3 )
		except:
			if self.peer.debug:
				traceback.print_exc()
		self.ui.rebuildLineEdit.clear()
				
