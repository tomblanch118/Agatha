import sys
import signal
import time, zmq
from agatha import debug

test_keep_going = True


def broker_signal_handler(signal, frame):
		debug('Broker process ending')
		global test_keep_going
		test_keep_going = False
		
		#context.destroy()

def PacketBroker(pq):
	#ZMQ context
	context = zmq.Context()
	
	#Set up as publisher
	debug("Setting up Packet Publisher")
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:5556")	
	
	
	#socket.send_pyobj();
	
	signal.signal(signal.SIGINT, broker_signal_handler)
	message = pq.get()

	if message:
		debug(message)

	global test_keep_going
	while test_keep_going:		
		if not pq.empty():
			socket.send(pq.get())
			#print(pq.get())
			#pq.task_done()
		time.sleep(0.01)
	context.destroy()
	print("Broker Done")
	