import json
import sys
import zmq
import time
import signal

interrupted = False

def signal_handler(signal, frame):
	global interrupted
	interrupted = True

	socket.close()
	unregister()
	sender.close()

def register():
	response = bytearray(b'\x00\x01')
	response.extend(map(ord,"DEBUG OUTPUT"))
	sender.send(response)
	
def unregister():
	response = bytearray(b'\x00\x02')
	response.extend(map(ord,"DEBUG OUTPUT"))
	sender.send(response)
	

def readsocket():
	while True:
		try:
			socks = dict(poller.poll(timeout=100))
		except KeyboardInterrupt:
			break
	
		if interrupted:
			break
			
		if socket in socks:
			dbgdata = socket.recv()
			if dbgdata[0] == 0 and dbgdata[1] == 0:
				print("Agatha says bye")

			else:
				dbgwords = dbgdata[2:].decode('utf8')
				print("DEBUG:",dbgwords)
	
	print("Done")
	
	
if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	
	print("Connecting to publisher")
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://localhost:5556")

	print("Connecting to push socket")
	#socket for sending things back to the broker
	sender = context.socket(zmq.PUSH)
	sender.connect("tcp://localhost:5558")
	#Set linger so that queued messages dont block us from exciting 
	sender.setsockopt(zmq.LINGER,500)

	print("Sending registration")
	register()
	#Try subscribing to multiple
	key = b'\00'.decode("utf-8","strict")	
	socket.setsockopt_string(zmq.SUBSCRIBE, key)

	poller = zmq.Poller()
	poller.register(socket,zmq.POLLIN)

	#Read and print debug
	readsocket()
