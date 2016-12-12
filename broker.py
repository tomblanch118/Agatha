import sys
import signal
import time, zmq
from agatha import debug

test_keep_going = True

def broker_signal_handler(signal, frame):
		debug('Broker process ending')
		global test_keep_going
		test_keep_going = False
		
#Do we need locks on nodeids to stop multiple processes trying to communicate with a node at the same time?
#

def PacketBroker(pq_rx,pq_tx):
	#ZMQ context
	context = zmq.Context()
	
	#Set up as publisher
	debug("Setting up Packet Publisher")
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:5556")	

	# Socket to receive messages from clients 
	receiver = context.socket(zmq.PULL)
	receiver.bind("tcp://*:5558")
	receiver.setsockopt(zmq.RCVTIMEO,10)
	
	#register signal handler
	signal.signal(signal.SIGINT, broker_signal_handler)
	
	#Pick the first message from the queue as Agatha will wait for us to empty the queue
	#before doing anything else
	message = pq_rx.get()

	#registered clients
	registered = {}
	
	#
	if message:
		debug(message)
		
	global test_keep_going
	while test_keep_going:		

		#Forward packets out to subscribers
		if not pq_rx.empty():
			socket.send(pq_rx.get())
			
		#catch any responses
		try:
			#Check what the response is, message or packet to transmit
			s = receiver.recv(zmq.NOBLOCK)
			if s[0] == 0:
				name = s[2:].decode('utf-8')
				if s[1] == 1:
					print("Registered: ",name)
					registered[name] = 1
				elif s[1] == 2:
					print("Unregistered: ",name)
					registered[name] = 0
			#Everything must be a packet so just forward it to the queue for agatha to write to the serial port
			else:
				pq_tx.put(s)
				
		except zmq.Again:
			pass		
		#Sleep a bit
		time.sleep(0.01)
		
	context.destroy()
	print("Broker Done")
	