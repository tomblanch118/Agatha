import json
import zmq
import time
import signal
from struct import unpack
from collections import namedtuple

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal.SIG_DFL);
	
	#Read packet format config file 
	print("Loading packet configs...")
	with open('data.txt','r') as handle:
		parse = json.load(handle)

	dic = {}
	#Constuct the format dictionary, indexed by packet id
	for x in parse.keys():
		print("Struct", parse[x][1],"found.")
		pid = parse[x][4]
		dic[pid] = (parse[x][0],parse[x][1],parse[x][2],parse[x][3])

	print("Connecting to publisher")
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect("tcp://localhost:5556")
	print("Connected")

	#key = b'\04'.decode("utf-8","strict")
	socket.setsockopt_string(zmq.SUBSCRIBE, "")
	
	while True:
		data = socket.recv()
		print("---------------")
		
		packetid = data[0]
		
		print(packetid)
		packetinfo = dic.get(packetid)
		
		if packetinfo:
		
			DataPacket = namedtuple(packetinfo[1],packetinfo[2])
			packet = (DataPacket._make(unpack(packetinfo[3],data)))._asdict()	
			
			for x in packet.keys():
				print(x,":",packet[x])
		else:
			print("Unknown packet...")
		

			
