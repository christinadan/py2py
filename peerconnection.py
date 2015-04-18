import socket
import struct
import threading
import time
import traceback

from peer import *

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
		