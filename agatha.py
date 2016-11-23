#Author: Tom Blanchard
import serial
import sys
import json
import time
from struct import *
from collections import namedtuple
from multiprocessing import Process, Queue, freeze_support
import signal

test_keep_going = True
#import logging, multiprocessing
#mpl = multiprocessing.log_to_stderr()
#mpl.setLevel(logging.DEBUG)

def signal_handler(signal, frame):
	print('Main process ending')
	broker.join()
	print('ended')
	sys.exit(0)

def PacketHandler(data,packetinfo):
	DataPacket = namedtuple(packetinfo[1],packetinfo[2])
	packet = (DataPacket._make(unpack(packetinfo[3],data)))._asdict()		

	packet_q.put(packet)

def PacketBroker(pq):
	def signal_handler2(signal, frame):
		print('Broker process ending')
		global test_keep_going
		test_keep_going = False
	
	signal.signal(signal.SIGINT, signal_handler2)
	message = pq.get()

	if message:
		print(message)

	global test_keep_going
	while test_keep_going:		
		if not pq.empty():
			print(pq.get())
			#pq.task_done()
		time.sleep(0.01)
	
	print("Broker Done")
	
		

def crc(data,crc):
	
	val = 0
	
	for v in data:
		val += v
	
	val = val % 256
	val = (val ^ 255)+1
	 
	print(ord(crc))
	print(val)
	 
	 
if __name__ == "__main__":

	freeze_support()
	
	print("AGATHA VERSION: The Mysterious Affair at Styles")

	packet_q = Queue()
	
	print("Starting broker process...")
	
	#packet_q = Queue()
	packet_q.put("<Packet broker online>")
	broker = Process(
			target=PacketBroker,
			args=(packet_q,)
	)
	
	#processes.append(p) 
	broker.start()

	while not packet_q.empty():
		pass


	#Packet info dictionary
	dic = {}

	signal.signal(signal.SIGINT, signal_handler)

	
	#Read packet format config file 
	print("Loading packet configs...")
	with open('data.txt','r') as handle:
		parse = json.load(handle)

	
	#Constuct the format dictionary, indexed by packet id
	for x in parse.keys():
		print("Struct", parse[x][1],"found.")
		pid = parse[x][4]
		dic[pid] = (parse[x][0],parse[x][1],parse[x][2],parse[x][3])
	
	#See if we were passed a comport
	comport = None	
	
	argv_index = 0
	for arg in sys.argv:
		argv_index += 1
		if arg == "-p" and argv_index < len(sys.argv):
			comport = sys.argv[argv_index]
	
	connected = False
	#Try to connect to serial port

	while not connected:
		if not comport:
			comport = input("Enter com port:")
		try:
			port = serial.Serial(comport, 115200, timeout=None)
			connected = True
		except serial.serialutil.SerialException:
			print("Failed to connect to",comport)
			comport = None

	print(port.name)

	prev = 0
	curr = 0

	while True:
		curr = port.read()

		if curr == b'\x55' and prev == b'\xAA':
			#print("Start of packet")
			
			tmp = port.read()
			packetid = ord(tmp)
			
			packetinfo = dic.get(packetid)
			
			if packetinfo:
				packetlength = packetinfo[0] - 1
				#print("Expected packet length:",packetlength)
				#Read packet length number of bytes
				data = port.read(packetlength)
				
				test = bytearray()
				test.extend(tmp)
				test.extend(data)
				
				
				c = port.read()
				crc(test,c)
				
				#crc = port
				##.read()
				
				if len(data) == packetlength:
					PacketHandler(test,packetinfo)
				else:
					print("Couldn't read correct number of bytes for this packet")
				
			else:
				print("Can't find this packet")
		prev = curr
	