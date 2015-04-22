from peer import *

PEERNAME = "NAME"	# request a peer's id
LISTPEERS = "LIST"	# delivers a list of peers upon request
INSERTPEER = "JOIN"	# request to join a group of peers
QUERY = "QUER"		# delivers file information asked for upon request
QRESPONSE = "RESP"	# lets peer know that another peer has what they are looking for
FILEGET = "FGET"	# delivers a file upon requests if the peer has said file
PEERQUIT = "QUIT"	# tell a peer that they are leaving the network
LISTFILES = "FILE"

REPLY = "REPL"		#Last message received successfully
ERROR = "ERRO"		#Last message resulted in an error



class PeerFileManager(Peer):
	#Child of peer with functionality to deal with files

	def __init__(self, serverport):
		#Initializes Peer, and then sets up files, router, and handlers 
		#that will be used to communicate between peers

		Peer.__init__(self, serverport)
	
		self.files = {}  # available files: name --> peerid mapping

		self.addRouter(self.__router)

		handlers = {LISTPEERS : self.__handle_listPeers,
					INSERTPEER : self.__handle_insertPeer,
					PEERNAME: self.__handle_peerName,
					QUERY: self.__handle_query,
					QRESPONSE: self.__handle_qResponse,
					FILEGET: self.__handle_fileGet,
					PEERQUIT: self.__handle_quit,
					LISTFILES : self.__handle_listFiles
					}

		for mt in handlers:
			self.addHandler(mt, handlers[mt])

	def __debug(self, msg):
	#Function for printing out debugging messages
		if self.debug:
			debug(msg)

	def __router(self, peerid):
	#Maps out all peers
		if peerid not in self.getPeerIds():
			return (None, None, None)
		else:
			rt = [peerid]
			rt.extend(self.peers[peerid])
			return rt

	def __handle_insertPeer(self, peerconn, data):
	#Inserts a peer that requested to join, and connects to said peer
		self.peerlock.acquire()
		try:
			try:
				peerid,host,port = data.split()

				# peerid = '%s:%s' % (host,port)
				if peerid not in self.getPeerIds() and peerid != self.myid:
					self.addPeer(peerid, host, port)
					self.__debug('added peer: %s' % peerid)
					peerconn.sendData(REPLY, 'Join: peer added: %s' % peerid)
				else:
					peerconn.sendData(ERROR, 'Join: peer already inserted %s'% peerid)
			except:
				self.__debug('invalid insert %s: %s' % (str(peerconn), data))
				peerconn.sendData(ERROR, 'Join: incorrect arguments')
		finally:
			self.peerlock.release()

	def __handle_listPeers(self, peerconn, data):
	#Responds to a LISTPEERS request
		self.peerlock.acquire()
		try:
			self.__debug('Listing peers %d' % self.numberOfPeers())
			peerconn.sendData(REPLY, '%d' % self.numberOfPeers())
			for pid in self.getPeerIds():
				host,port = self.getPeer(pid)
				peerconn.sendData(REPLY, '%s %s %d' % (pid, host, port))
		finally:
			self.peerlock.release()

	def __handle_peerName(self, peerconn, data):
	#Replies to NAME message type, Does not use any data received
		peerconn.sendData(REPLY, self.myid)

	def __handle_query(self, peerconn, data):
	#Takes QEURY message and handles in a separate thread

		# self.peerlock.acquire()
		try:
			peerid, key, ttl = data.split()
			peerconn.sendData(REPLY, 'Query ACK: %s' % key)
		except:
			self.__debug('invalid query %s: %s' % (str(peerconn), data))
			peerconn.sendData(ERROR, 'Query: incorrect arguments')
		# self.peerlock.release()

		t = threading.Thread(target=self.__processQuery, 
					  args=[peerid, key, int(ttl)])
		t.start()

	def __processQuery(self, peerid, key, ttl):
	#Will either respond with the file that was found, or will ask all neighbors for the file.
		for fname in self.files.keys():
			if key in fname:
				fpeerid = self.files[fname]
				if not fpeerid:   # local files mapped to None
					fpeerid = self.myid
				host,port = peerid.split(':')
				# can't use sendToPeer here because peerid is not necessarily
				# an immediate neighbor
				self.connectAndSend(host, int(port), QRESPONSE, 
							 '%s %s' % (fname, fpeerid),
							 pid=peerid)
				return
		# will only reach here if key not found... in which case
		# propagate query to neighbors
		if ttl > 0:
			msgdata = '%s %s %d' % (peerid, key, ttl - 1)
			for nextpid in self.getPeerIds():
				self.sendToPeer(nextpid, QUERY, msgdata)

	def __handle_qResponse(self, peerconn, data):
	#Formats the response for a query, and then adds the peer name to the file list

		try:
			fname, fpeerid = data.rsplit( " ", 1 )
			if fname in self.files:
				self.__debug('Can\'t add duplicate file %s %s' % 
					  (fname, fpeerid))
			else:
				self.files[fname] = fpeerid
		except:
			#if self.debug:
				traceback.print_exc()

	def __handle_fileGet(self, peerconn, data):
	#Responds to a FILEGET message by sending the requested file

		fname = data
		if fname not in self.files:
			self.__debug('File not found %s' % fname)
			peerconn.sendData(ERROR, 'File not found')
			return
		try:
			fd = file(fname, 'rb')
			filedata = ''
			while True:
				data = fd.read(2048)
				if not len(data):
					break;
				filedata += data
			fd.close()
		except:
			self.__debug('Error reading file %s' % fname)
			peerconn.sendData(ERROR, 'Error reading file')
			return
	
		peerconn.sendData(REPLY, filedata)

	def __handle_quit(self, peerconn, data):
	#Disconnects from a peer after receiving the quit message

		self.peerlock.acquire()
		try:
			peerid = data.lstrip().rstrip()
			if peerid in self.getPeerIds():
				msg = 'Quit: peer removed: %s' % peerid 
				self.__debug(msg)
				peerconn.sendData(REPLY, msg)
				self.removePeer(peerid)
			else:
				msg = 'Quit: peer not found: %s' % peerid 
				self.__debug(msg)
				peerconn.sendData(ERROR, msg)
		finally:
			self.peerlock.release()

	def __handle_listFiles(self, peerconn, data):
	#Sends a list of files upon request

		self.peerlock.acquire()
		try:
			self.__debug('Listing %d files' % len(self.files))
			peerconn.sendData(REPLY, '%d' % len(self.files))
			for fname in self.files.keys():
				if filename == '(local)'
					self.__debug('%s' % file)
					peerconn.sendData(REPLY, '%s' % (fname))
		finally:
			self.peerlock.release()

	def buildPeers(self, host, port, hops=1):
	#Builds local peer list using a depth first search method

		#Base case for recursion
		if not hops:
			return

		peerid = None

		self.__debug("Building peers from (%s,%s)" % (host,port))

		try:
			_, peerid = self.connectAndSend(host, port, PEERNAME, '')[0]

			self.__debug("Contacted " + peerid)
			#Ask peer we're contacting to add us to their peerlist
			resp = self.connectAndSend(host, port, INSERTPEER, 
										'%s %s %d' % (self.myid, 
												  self.serverhost, 
												  self.serverport))[0]
			self.__debug(str(resp))
			#If they don't respond to us the break
			if (resp[0] != REPLY) or (peerid in self.getPeerIds()):
				return
			#If they respond then add them to our list as well
			self.addPeer(peerid, host, port)

			#Do recursive depth first search to add more peers
			#Request a list of peers from whoever we're talking to 
			resp = self.connectAndSend(host, port, LISTPEERS, '',
										pid=peerid)
			#If their list is > 1 (i.e. contains more than just us) then parse their list
			#and call buildPeers on each peer in list
			if len(resp) > 1:
				resp.reverse()
				resp.pop()	# get rid of header count reply
				while len(resp):
					nextpid,host,port = resp.pop()[1].split()
					#Don't try to talk to ourselves
					if nextpid != self.myid:
						self.buildPeers(host, port, hops - 1)
		except:
			#If something breaks throw peer away
			if self.debug:
				traceback.print_exc()
			self.removePeer(peerid)
			
	def buildFiles(self):
		#Builds local file list by going through our peer list and requesting a file list from each one
		self.__debug("Building files")

		try:
			for pid in self.getPeerIds():
				host,port = self.getPeer(pid)

				self.__debug("Contacted " + pid)
				
				#Request a list of files from whoever we're talking to 
				resp = self.connectAndSend(host, port, LISTFILES, '',
											pid)
				#If their list is > 0 (i.e. contains some files) then parse their list
				#and add each individual file to our own list
				if len(resp) > 0:
					resp.reverse()
					resp.pop()	# get rid of header count reply
					while len(resp):
						filename = resp.pop()[1]
						self.files[filename] = pid
		except:
			#If something breaks get out
			if self.debug:
				traceback.print_exc()

	def addLocalFile(self, filename):
	#Updates filelist to notify user that the file is now local
		self.files[filename] = None
		self.__debug("Added local file %s" % filename)
	
