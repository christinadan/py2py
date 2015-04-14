import sys
import threading

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
		self.ui.actionUpload.triggered.connect( self.fileSelect )
		self.ui.actionRefresh.triggered.connect( self.onRefresh )

		self.connectionPopup()
		#Add signal to do the rest of this in another function on connection dialog close event
		#Initialize connection settings
		self.peer = FilerPeer( int(self.connectionDialog.localPort) )

		#check IP; if good IP, connect; else, use a default
		self.peer.buildpeers( self.connectionDialog.peerHost, int(self.connectionDialog.peerPort), hops=hops )
		self.updatePeerList()

		t = threading.Thread( target = self.peer.mainloop, args = [] )
		t.start()

		self.peer.startstabilizer( self.peer.checklivepeers, 3 )
		#self.peer.startstabilizer( self.onRefresh, 3 )
		#self.after( 3000, self.onTimer )
		
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
			self.peer.addlocalfile( filename )
		self.updateFileList()

	def onTimer( self ):
		#Refresh every 3 seconds
		try:
			# Do things
			self.onRefresh()
		finally:
			QTimer.singleShot(3000, onTimer)
		
	def closeEvent(self, event):
		self.peer.shutdown = True
		event.accept() # let the window close
		
	def updatePeerList( self ):
		#If Peer list display has data, delete it then repopulate from self.peer.getpeerids()
		if self.ui.peerList.count() > 0:
			self.ui.peerList.clear()
		for p in self.peer.getpeerids():
			self.ui.peerList.insertItem( self.ui.peerList.currentRow(), p )
			
	def updateFileList( self ):
		#If GUI file display has data, delete it then repopulate from self.peer.files
		if self.ui.fileList.rowCount() > 0:
			self.ui.fileList.clearContents()

		row = 0
		for f in self.peer.files:
			p = self.peer.files[f]
			if not p:
				p = '(local)'

			hostItem = QTableWidgetItem(p)
			fileItem = QTableWidgetItem(f)
			if row == 0:
				self.ui.fileList.insertRow(row)

			self.ui.fileList.setItem(row, 0, hostItem)
			self.ui.fileList.setItem(row, 1, fileItem)
			row = row + 1
		
	def onSearch(self):
		#Gets filename from Search field and queries the network using self.peer.sendtopeer
		'''key = self.searchEntry.get()
		self.searchEntry.delete( 0, len(key) )

		for p in self.peer.getpeerids():
			self.peer.sendtopeer( p, QUERY, "%s %s 4" % ( self.peer.myid, key ) )'''
	
	def onFetch(self):
		#Get currently selected file from GUI and retrieve said file from network
		'''sels = self.fileList.curselection()
		if len(sels)==1:
			sel = self.fileList.get(sels[0]).split(':')
			if len(sel) > 2:  # fname:host:port
				fname,host,port = sel
				resp = self.peer.connectandsend( host, port, FILEGET, fname )
				if len(resp) and resp[0][0] == REPLY:
					fd = file( fname, 'wb' )
					fd.write( resp[0][1] )
					fd.close()
					self.peer.files[fname] = None  # because it's local now'''
	
	def onRemove(self):
		#Get currently selected peer from GUI and remove said peer, sending PEERQUIT msg
		'''sels = self.peerList.curselection()
		if len(sels)==1:
			peerid = self.peerList.get(sels[0])
			self.peer.sendtopeer( peerid, PEERQUIT, self.peer.myid )
			self.peer.removepeer( peerid )'''
	
	def onRefresh(self):
		#Update peer and file list
		self.updatePeerList()
		self.updateFileList()
	
	def onRebuild(self):
		#Get peerid from rebuild field and rebuild peer list using self.peer.buildpeers
		'''peerid = self.rebuildEntry.get()
		self.rebuildEntry.delete( 0, len(peerid) )
		peerid = peerid.lstrip().rstrip()
		try:
			host,port = peerid.split(':')
			#print "doing rebuild", peerid, host, port
			self.peer.buildpeers( host, port, hops=3 )
		except:
			if self.peer.debug:
				traceback.print_exc()
				#         for peerid in self.peer.getpeerids():
				#            host,port = self.peer.getpeer( peerid )'''
				
				
