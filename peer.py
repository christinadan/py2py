#!/usr/bin/python

#peer.py

#Based off tutorial found at: http://cs.berry.edu/~nhamid/p2p/

import socket
import struct
import threading
import time
import traceback

from peerconnection import *


def debug( msg ):
	#Print current thread and debug parameter to the console
	print "[%s] %s" % ( str(threading.currentThread().getName()), msg )

class Peer:

	def __init__( self, serverport ):
	
		self.debug = 1	#Flag for debugging
		self.serverport = int(serverport) #Port obtained from GUI
		s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )	#Ping google to get our IP address
		s.connect( ( "www.google.com", 80 ) )
		self.serverhost = s.getsockname()[0]
		s.close()
		self.myid = '%s:%d' % (self.serverhost, self.serverport) #concat ip and port to define peerId
		self.peerlock = threading.Lock()	#Define a thread lock attribute
		self.peers = {}	#Define empty list for peers
		self.shutdown = False	#Flag to determine when to gracefully exit
		self.handlers = {}	#Handlers defined later in filer.py
		self.router = None

	def __debug( self, msg ):
		#Override debug class
		if self.debug:
			debug( msg )

	def __handlePeer( self, clientsock ):
	
		self.__debug( 'New child ' + str(threading.currentThread().getName()) )
		self.__debug( 'Connected ' + str(clientsock.getpeername()) )

		host, port = clientsock.getpeername()
		peerconn = PeerConnection( None, host, port, clientsock, debug=False )	#Create a new connection with peer
		
		try:
			msgtype, msgdata = peerconn.recvData()
			if msgtype: msgtype = msgtype.upper()
			if msgtype not in self.handlers:	#Check if message type is in handlers
				self.__debug( 'Not handled: %s: %s' % (msgtype, msgdata) )
			else:
				self.__debug( 'Handling peer msg: %s: %s' % (msgtype, msgdata) )
				self.handlers[ msgtype ]( peerconn, msgdata )
		except KeyboardInterrupt:
			raise
		except:
			if self.debug:
				traceback.print_exc()
		
		self.__debug( 'Disconnecting ' + str(clientsock.getpeername()) )
		peerconn.close()
		#End handlePeer

	def __runStabilizer( self, stabilizer, delay ):
		while not self.shutdown:
			stabilizer()
			time.sleep( delay )

	def startStabilizer( self, stabilizer, delay ):	#Create a stabilizer background function in a separate thread
		t = threading.Thread( target = self.__runStabilizer, args = [ stabilizer, delay ] )
		t.start()

	def addHandler( self, msgtype, handler ):
		#Add handler to list if it's 4 characters long
		assert len(msgtype) == 4
		self.handlers[ msgtype ] = handler

	def addRouter( self, router ):
		self.router = router

	def addPeer( self, peerid, host, port ):
		#Adds peer with peerId defined as ip:port
		if peerid not in self.peers:
			self.peers[ peerid ] = (host, int(port))
			return True
		else:
			return False

	def getPeer( self, peerid ):
		#Return peerid if it's in list of peers
		assert peerid in self.peers
		return self.peers[ peerid ]

	def removePeer( self, peerid ):
		#Delete peer from list
		if peerid in self.peers:
			del self.peers[ peerid ]

	def getPeerIds( self ):
		#Returns a list of all peer ids
		return self.peers.keys()

	def numberOfPeers( self ):
		#Returns length of peer list
		return len(self.peers)

	def makeServerSocket( self, port, backlog=5 ):
		#Create a listening socket for incoming connections
		s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
		s.bind( ( '', port ) )
		s.listen( backlog )
		return s

	def sendToPeer( self, peerid, msgtype, msgdata, waitreply=True ):
		#Send specified message to peer 
		if self.router:
			nextpid, host, port = self.router( peerid )
		if not self.router or not nextpid:
			self.__debug( 'Unable to route %s to %s' % (msgtype, peerid) )
			return None
		return self.connectAndSend( host, port, msgtype, msgdata, pid=nextpid, waitreply=waitreply )
		
	def connectAndSend( self, host, port, msgtype, msgdata, pid=None, waitreply=True ):
		#Create a new PeerConnection with said peer and send message, waiting for response
		msgreply = []
		try:
			peerconn = PeerConnection( pid, host, port, debug=self.debug )
			peerconn.sendData( msgtype, msgdata )
			self.__debug( 'Sent %s: %s' % (pid, msgtype) )
			
			if waitreply:
				onereply = peerconn.recvData()
				while (onereply != (None,None)):
					msgreply.append( onereply )
					self.__debug( 'Got reply %s: %s' % ( pid, str(msgreply) ) )
					onereply = peerconn.recvData()
			peerconn.close()
		except KeyboardInterrupt:
			raise
		except:
			if self.debug:
				traceback.print_exc()
		
		return msgreply
		#end connectAndSend

	def checkLivePeers( self ):
		#Used as stabilizer function to ping a peer, if no reponse is received, then peer is removed from list
		todelete = []
		for pid in self.peers:
			isconnected = False
			try:
				self.__debug( 'Check live %s' % pid )
				host,port = self.peers[pid]
				peerconn = PeerConnection( pid, host, port, debug=self.debug )
				peerconn.sendData( 'PING', '' )
				isconnected = True
			except:
				self.__debug( 'Adding to delete %s' % pid )
				todelete.append( pid )
			if isconnected:
				peerconn.close()

		self.peerlock.acquire()
		try:
			for pid in todelete: 
				if pid in self.peers: 
					del self.peers[pid]
					self.__debug( 'Deleting %s' % pid )
		finally:
			self.peerlock.release()
		#end checkLivePeers

	def mainLoop( self ):
		#main loop that creates server socket and listens for incoming connectiosn until shutdown
		s = self.makeServerSocket( self.serverport )
		s.settimeout(2)
		self.__debug( 'Server started: %s (%s:%d)'% ( self.myid, self.serverhost, self.serverport ) )
		
		while not self.shutdown:
			try:
				self.__debug( 'Listening for connections...' )
				clientsock, clientaddr = s.accept()
				clientsock.settimeout(None)

				t = threading.Thread( target = self.__handlePeer, args = [ clientsock ] )
				t.start()
			except KeyboardInterrupt:
				print 'KeyboardInterrupt: stopping mainLoop'
				self.shutdown = True
				continue
			except:
				if self.debug:
					traceback.print_exc()
					continue
		#end while loop
		self.__debug( 'Main loop exiting' )

		s.close()

		#end mainLoop

#end Peer class

class PeerConnection:
	
	def __init__( self, peerid, host, port, sock=None, debug=False ):
		# any exceptions thrown upwards
		self.id = peerid
		self.debug = debug

		if not sock:
			self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.s.settimeout(1)
			self.s.connect( ( host, int(port) ) )
			self.s.settimeout(None)
		else:
			self.s = sock

		self.sd = self.s.makefile( 'rw', 0 )
	
	def __makeMsg( self, msgtype, msgdata ):
		#Constructs message into packet to be sent
		msglen = len(msgdata)
		msg = struct.pack( "!4sL%ds" % msglen, msgtype, msglen, str( msgdata ) )
		return msg

	def __debug( self, msg ):
		#Override debug class
		if self.debug:
			debug( msg )

	def sendData( self, msgtype, msgdata ):
		#Send message through peer connection
		try:
			msg = self.__makeMsg( msgtype, msgdata )
			self.sd.write( msg )
			self.sd.flush()
		except KeyboardInterrupt:
			raise
		except:
			if self.debug:
				traceback.print_exc()
			return False
		return True
		
	def recvData( self ):
		#Receive message through peer connection
		try:
			msgtype = self.sd.read( 4 )
			if not msgtype: return (None, None)
			
			lenstr = self.sd.read( 4 )
			msglen = int(struct.unpack( "!L", lenstr )[0])
			msg = ""

			while len(msg) != msglen:
				data = self.sd.read( min(2048, msglen - len(msg)) )
				if not len(data):
					break
				msg += data

			if len(msg) != msglen:
				return (None, None)

		except KeyboardInterrupt:
			raise
		except:
			if self.debug:
				traceback.print_exc()
			return (None, None)

		return ( msgtype, msg )
		#End recvData

	def close( self ):
		#Close peer connection
		self.s.close()
		self.s = None
		self.sd = None
		
	def __str__( self ):
		return "|%s|" % peerid
		