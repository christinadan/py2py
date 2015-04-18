#!/usr/bin/python

#filer.py

#Based off tutorial found at: http://cs.berry.edu/~nhamid/p2p/

from peer import *

PEERNAME = "NAME"   # request a peer's canonical id
LISTPEERS = "LIST"
INSERTPEER = "JOIN"
QUERY = "QUER"
QRESPONSE = "RESP"
FILEGET = "FGET"
PEERQUIT = "QUIT"
LISTFILES = "FILE"

REPLY = "REPL"
ERROR = "ERRO"


# Assumption in this program:
#   peer id's in this application are just "host:port" strings

#==============================================================================
class FilerPeer(Peer):
#==============================================================================
    """ Implements a file-sharing peer-to-peer entity based on the generic
    P2P framework.

    """

    #--------------------------------------------------------------------------
    def __init__(self, serverport):
    #--------------------------------------------------------------------------
	""" Initializes the peer to support connections with an unlimited number
	of peers, with its server listening on the specified port. Also sets
	the dictionary of local files to empty and adds handlers to the 
	Peer framework.

	"""
	Peer.__init__(self, serverport)
	
	self.files = {}  # available files: name --> peerid mapping

	self.addRouter(self.__router)

	handlers = {LISTPEERS : self.__handle_listpeers,
		    INSERTPEER : self.__handle_insertpeer,
		    PEERNAME: self.__handle_peername,
		    QUERY: self.__handle_query,
		    QRESPONSE: self.__handle_qresponse,
		    FILEGET: self.__handle_fileget,
		    PEERQUIT: self.__handle_quit,
			LISTFILES : self.__handle_listfiles
		   }
	for mt in handlers:
	    self.addHandler(mt, handlers[mt])

    # end FilerPeer constructor



    #--------------------------------------------------------------------------
    def __debug(self, msg):
    #--------------------------------------------------------------------------
	if self.debug:
	    debug(msg)



    #--------------------------------------------------------------------------
    def __router(self, peerid):
    #--------------------------------------------------------------------------
	if peerid not in self.getPeerIds():
	    return (None, None, None)
	else:
	    rt = [peerid]
	    rt.extend(self.peers[peerid])
	    return rt



    #--------------------------------------------------------------------------
    def __handle_insertpeer(self, peerconn, data):
    #--------------------------------------------------------------------------
	""" Handles the INSERTPEER (join) message type. The message data
	should be a string of the form, "peerid  host  port", where peer-id
	is the canonical name of the peer that desires to be added to this
	peer's list of peers, host and port are the necessary data to connect
	to the peer.

	"""
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
		    peerconn.sendData(ERROR, 'Join: peer already inserted %s'
				       % peerid)
	    except:
		self.__debug('invalid insert %s: %s' % (str(peerconn), data))
		peerconn.sendData(ERROR, 'Join: incorrect arguments')
	finally:
	    self.peerlock.release()

    # end handle_insertpeer method



    #--------------------------------------------------------------------------
    def __handle_listpeers(self, peerconn, data):
    #--------------------------------------------------------------------------
	""" Handles the LISTPEERS message type. Message data is not used. """
	self.peerlock.acquire()
	try:
	    self.__debug('Listing peers %d' % self.numberOfPeers())
	    peerconn.sendData(REPLY, '%d' % self.numberOfPeers())
	    for pid in self.getPeerIds():
		host,port = self.getPeer(pid)
		peerconn.sendData(REPLY, '%s %s %d' % (pid, host, port))
	finally:
	    self.peerlock.release()



    #--------------------------------------------------------------------------
    def __handle_peername(self, peerconn, data):
    #--------------------------------------------------------------------------
	""" Handles the NAME message type. Message data is not used. """
	peerconn.sendData(REPLY, self.myid)



    # QUERY arguments: "return-peerid key ttl"
    #--------------------------------------------------------------------------
    def __handle_query(self, peerconn, data):
    #--------------------------------------------------------------------------
	""" Handles the QUERY message type. The message data should be in the
	format of a string, "return-peer-id  key  ttl", where return-peer-id
	is the name of the peer that initiated the query, key is the (portion
	of the) file name being searched for, and ttl is how many further 
	levels of peers this query should be propagated on.

	"""
	# self.peerlock.acquire()
	try:
	    peerid, key, ttl = data.split()
	    peerconn.sendData(REPLY, 'Query ACK: %s' % key)
	except:
	    self.__debug('invalid query %s: %s' % (str(peerconn), data))
	    peerconn.sendData(ERROR, 'Query: incorrect arguments')
	# self.peerlock.release()

	t = threading.Thread(target=self.__processquery, 
			      args=[peerid, key, int(ttl)])
	t.start()



    # 
    #--------------------------------------------------------------------------
    def __processquery(self, peerid, key, ttl):
    #--------------------------------------------------------------------------
	""" Handles the processing of a query message after it has been 
	received and acknowledged, by either replying with a QRESPONSE message
	if the file is found in the local list of files, or propagating the
	message onto all immediate neighbors.

	"""
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



    #--------------------------------------------------------------------------
    def __handle_qresponse(self, peerconn, data):
    #--------------------------------------------------------------------------
	""" Handles the QRESPONSE message type. The message data should be
	in the format of a string, "file-name  peer-id", where file-name is
	the file that was queried about and peer-id is the name of the peer
	that has a copy of the file.

	"""
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



    #--------------------------------------------------------------------------
    def __handle_fileget(self, peerconn, data):
    #--------------------------------------------------------------------------
	""" Handles the FILEGET message type. The message data should be in
	the format of a string, "file-name", where file-name is the name
	of the file to be fetched.

	"""
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



    #--------------------------------------------------------------------------
    def __handle_quit(self, peerconn, data):
    #--------------------------------------------------------------------------
	""" Handles the QUIT message type. The message data should be in the
	format of a string, "peer-id", where peer-id is the canonical
	name of the peer that wishes to be unregistered from this
	peer's directory.

	"""
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

		
	#--------------------------------------------------------------------------
    def __handle_listfiles(self, peerconn, data):
    #--------------------------------------------------------------------------
	""" Handles the LISTFILES message type. Message data is not used. """
	#NOT YET WORKING
	self.peerlock.acquire()
	try:
	    self.__debug('Listing files %d' % self.numberoffiles())
	    peerconn.sendData(REPLY, '%d' % self.numberoffiles())
	    for fname in self.files.keys():
		peerconn.sendData(REPLY, '%s' % (fname))
	finally:
	    self.peerlock.release()


    # precondition: may be a good idea to hold the lock before going
    #               into this function
    #--------------------------------------------------------------------------
    def buildpeers(self, host, port, hops=1):
    #--------------------------------------------------------------------------
	""" buildpeers(host, port, hops) 

	Attempt to build the local peer list, using a simple depth-first search given an
	initial host and port as starting point. The depth of the
	search is limited by the hops parameter.

	"""
	if not hops:
	    return

	peerid = None

	self.__debug("Building peers from (%s,%s)" % (host,port))

	try:
	    _, peerid = self.connectAndSend(host, port, PEERNAME, '')[0]

	    self.__debug("contacted " + peerid)
	    resp = self.connectAndSend(host, port, INSERTPEER, 
					'%s %s %d' % (self.myid, 
						      self.serverhost, 
						      self.serverport))[0]
	    self.__debug(str(resp))
	    if (resp[0] != REPLY) or (peerid in self.getPeerIds()):
		return

	    self.addPeer(peerid, host, port)

	    # do recursive depth first search to add more peers
	    resp = self.connectAndSend(host, port, LISTPEERS, '',
					pid=peerid)
	    if len(resp) > 1:
		resp.reverse()
		resp.pop()    # get rid of header count reply
		while len(resp):
		    nextpid,host,port = resp.pop()[1].split()
		    if nextpid != self.myid:
			self.buildpeers(host, port, hops - 1)
	except:
	    if self.debug:
		traceback.print_exc()
	    self.removePeer(peerid)



    #--------------------------------------------------------------------------
    def addlocalfile(self, filename):
    #--------------------------------------------------------------------------
	""" Registers a locally-stored file with the peer. """
	self.files[filename] = None
	self.__debug("Added local file %s" % filename)
	
	#--------------------------------------------------------------------------
    def numberoffiles( self ):
    #--------------------------------------------------------------------------
	""" Return the number of known peer's. """
	return len(self.files)
