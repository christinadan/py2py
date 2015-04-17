import sys
import threading
import os

from PyQt5.Qt import *
from Generated.ui_mainwindow import Ui_MainWindow
from connectiondialog import ConnectionDialog
from random import *
from filer import *

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
		self.peer = FilerPeer( int(self.connectionDialog.localPort) )

		#check IP; if good IP, connect; else, use a default
		self.peer.buildpeers( self.connectionDialog.peerHost, int(self.connectionDialog.peerPort), hops=hops )
		self.updatePeerList()
		self.ui.portLabel.setText('Server Port: ' + self.connectionDialog.localPort)

		t = threading.Thread( target = self.peer.mainloop, args = [] )
		t.start()

		self.peer.startstabilizer( self.peer.checklivepeers, 3 )
		#self.peer.startstabilizer( self.onRefresh, 3 )
		self.onTimer()

	def connectSignals(self):
		self.ui.actionUpload.triggered.connect( self.fileSelect )
		self.ui.actionRefresh.triggered.connect( self.onRefresh )
		self.ui.actionDownload.triggered.connect( self.onDownload )
		self.ui.fetchButton.clicked.connect( self.onDownload )
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
		fileDialog.exec_()
		filename = fileDialog.selectedFiles()[0]
		if filename != "" and filename:
			self.peer.addlocalfile( str( filename ) )
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
		#If Peer list display has data, delete it then repopulate from self.peer.getpeerids()
		if len( self.ui.peerList.selectedItems() ) > 0:
			selectedItem = self.ui.peerList.selectedItems()[0].text()
			print selectedItem
		else:
			selectedItem = ""

		if self.ui.peerList.count() > 0:
			self.ui.peerList.clear()

		for p in self.peer.getpeerids():
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

	def onSearch(self):
		#Gets filename from Search field and queries the network using self.peer.sendtopeer
		self.searchTerm = self.ui.searchLineEdit.text()

		for p in self.peer.getpeerids():
			self.peer.sendtopeer( p, QUERY, "%s %s 4" % ( self.peer.myid, str( self.searchTerm ) ) )
	
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
				resp = self.peer.connectandsend( host, int(port), FILEGET, str( fileItemPath ) )
				if len( resp ) and resp[0][0] == REPLY:
					if not os.path.exists('Downloads'):
						os.makedirs('Downloads')
					curDir = os.getcwd()
					os.chdir('Downloads')
					fd = file( fileItem, 'wb')
					fd.write( resp[0][1] )
					fd.close()
					self.peer.files[str( fileItemPath )] = None
					os.chdir( curDir )
	
	def onRefresh(self):
		#Update peer and file list
		self.updatePeerList()
		self.updateFileList()
	
	def onRebuild(self):
		#Get peerid from rebuild field and rebuild peer list using self.peer.buildpeers
		peer = self.ui.rebuildLineEdit.text()
		peer = peer.lstrip().rstrip()

		try:
			if peer != "":
				host,port = peer.split(':')
				self.peer.buildpeers( host, int(port), hops=3 )
		except:
			if self.peer.debug:
				traceback.print_exc()
				#         for peerid in self.peer.getpeerids():
				#            host,port = self.peer.getpeer( peerid )
		self.ui.rebuildLineEdit.clear()
				
				
