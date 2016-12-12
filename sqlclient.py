import json
import sys
import zmq
import time
import signal
from struct import unpack
from collections import namedtuple
#import agatha 

"""
import logging, multiprocessing
mpl = multiprocessing.log_to_stderr()
mpl.setLevel(logging.DEBUG)
"""

interrupted = False
def debug(message):
	if dbg==True:
		print(message)
		
def read_struct_config(config_filename):
#Read packet format config file 
	print("Loading packet configs...")
	with open(config_filename,'r') as handle:
		parse = json.load(handle)

	dic = {}
	#Constuct the format dictionary, indexed by packet id
	for x in parse.keys():
		print("Struct", parse[x][1],"found.")
		pid = parse[x][4]
		dic[pid] = (parse[x][0],parse[x][1],parse[x][2],parse[x][3])
		
	return dic
	
def signal_handler(signal, frame):
	global interrupted
	interrupted = True
	socket.close()
	response = bytearray(b'\x00\x02')
	response.extend(map(ord,"SQLCLIENT"))
	sender.send(response)
	sender.close()
	
	
	
if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	
	dic = read_struct_config('data.txt')

	print("Connecting to publisher")
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://localhost:5556")
	print("Connected")

	#socket for sending things back to the broker
	sender = context.socket(zmq.PUSH)
	sender.connect("tcp://localhost:5558")
	#Set linger so that queued messages dont block us from exciting 
	sender.setsockopt(zmq.LINGER,500)
	
	#Try subscribing to multiple
	key = b'\01'.decode("utf-8","strict")
	key2 = b'\02'.decode("utf-8","strict")
	socket.setsockopt_string(zmq.SUBSCRIBE, key)
	socket.setsockopt_string(zmq.SUBSCRIBE, key2)
	
	#generate registration packet and send
	response = bytearray(b'\x00\x01')
	response.extend(map(ord,"SQLCLIENT"))
	
	sender.send(response)
	
	while True:
		try:
			data = socket.recv(zmq.NOBLOCK)
			print("---------------")
			
			packetid = data[0]
			
			#print(packetid)
			packetinfo = dic.get(packetid)
			
			if packetinfo:
				#Data contains the packet plus the rssi and nodeid at the end, we need to strip them off before unpacking.
				DataPacket = namedtuple(packetinfo[1],packetinfo[2])
				packet = (DataPacket._make(unpack(packetinfo[3],data[0:-2])))._asdict()	
				
				
				for x in packet.keys():
					print(x,":",packet[x])
				index  = len(data)
				print("id:",data[index-2],"\nrssi:",data[index-1])
	
				response = bytearray(b'\x01\xff')
				sender.send(response)
				
			else:
				print("Unknown packet...")

		except zmq.ZMQError:
			pass
		
		if interrupted:
			break
		time.sleep(0.005)
	print("Finished")
	sys.exit(1)